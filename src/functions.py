import PyPDF2
import re
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer
from language_tool_python import LanguageTool
from transformers import AutoTokenizer, BartForConditionalGeneration
import torch

paper_model_path = "iter_trained_model"
text_model_path = "facebook/bart-large-cnn"
tokenizer_path = "tokenizer"

device = "cuda" if torch.cuda.is_available() else "cpu"

def remove_section_headers(text):
    # Define the regular expression pattern to match sequences like "1. xy"
    section_patterns = [
        # Digits
        r'\b\d+\.\s+\w+\b',
        # Roman Numerals
        r'\b[IVXLCDM]+\.\s+\w+\b'
    ]

    # Combine patterns into a single regex pattern
    pattern = '|'.join(section_patterns)

    # Use re.sub to replace matched sequences with an empty string
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

def exclude_header_footer(text):
    # Split text into sentences using regex
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    # No of sentences to exclude in header
    num_sentences_to_exclude_header = int( len(sentences) * 0.05 )
    # No of sentences to exclude in footer
    num_sentences_to_exclude_footer = int(len(sentences) * 0.1 )
    
    # Exclude the header and footer  of page
    excluded_sentences = sentences[num_sentences_to_exclude_header:-num_sentences_to_exclude_footer]
    
    # Rejoin the remaining sentences
    remaining_text = ' '.join(excluded_sentences)
    
    return remaining_text

def remove_citations(text):
    # Define patterns for common citation formats
    citation_patterns = [
        # Match citations like "[1]", "[12]", "[123]", etc.
        r'\[\d+\]',
        
        # Match citations like "(Author, Year)", "(Author et al., Year)", "(Author Year)", etc.
        r'\(\w+(?: et al.)?, \d{4}\)',
        
        # Match citations like "[Author et al., Year]", "[Author, Year]", etc.
        r'\[\w+(?: et al.)?, \d{4}\]'
    ]
    
    # Combine patterns into a single regex pattern
    combined_pattern = '|'.join(citation_patterns)
    
    # Remove citations from the text using the regex pattern
    cleaned_text = re.sub(combined_pattern, '', text)
    
    return cleaned_text

def replace_multiple_whitespace(text):
    # Define the regular expression pattern to match multiple whitespace characters
    pattern = r'\s+'
    
    # Use re.sub to replace multiple whitespace characters with a single whitespace character
    cleaned_text = re.sub(pattern, ' ', text)
    
    return cleaned_text

def fix_grammar(text):
    tool = LanguageTool('en-US')

    # Check for grammatical errors
    matches = tool.check(text)
    # Fix grammatical errors
    corrected_text = tool.correct(text)

    return corrected_text

def preprocess_text(text):
    # replace new line character with space
    text = text.replace("\n"," ")

    # removing extra whitespaces
    text = replace_multiple_whitespace(text)

    # remove citations
    text = remove_citations(text)

    #remove section heading
    text = remove_section_headers(text)

    return text

def get_paper_content(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        full_text = []

        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            page_content = page.extract_text()
            cleaned_content = preprocess_text(page_content)
            cleaned_content = exclude_header_footer(cleaned_content)
            full_text.append(cleaned_content)

        final_text = '\n'.join(full_text)

        return final_text

def generate_summary_paper(text, min_summary_length=128, max_summary_length=1024, overlap_percentage=35):
    text = fix_grammar(text)
    
    model = BartForConditionalGeneration.from_pretrained(paper_model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path,device=device)

    tokenized_text = tokenizer.encode(text, return_tensors="pt", truncation=False).to(device)
    # Calculate overlap size
    max_tokens = 1024
    overlap_size = int(max_tokens * overlap_percentage / 100)

    # Generate summaries with overlapping chunks
    summaries = []
    for i in range(0, tokenized_text.size(1) - max_tokens + 1, max_tokens - overlap_size):
        start = i
        end = min(i + max_tokens, tokenized_text.size(1))
        chunk = tokenized_text[:, start:end]
        summary_ids = model.generate(chunk, min_length=min_summary_length, max_length=max_summary_length, num_beams=16, early_stopping=True, length_penalty=0.8, repetition_penalty=1.5)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)

    # Concatenate summaries to create the final summary
    final_summary = " ".join(summaries)
    final_summary = final_summary.replace("\n"," ")
    return fix_grammar(final_summary)

def generate_summary_text(text, min_summary_length=128, max_summary_length=1024, overlap_percentage=35):
    # Tokenize the input text
    text = fix_grammar(text)

    model = BartForConditionalGeneration.from_pretrained(text_model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    tokenized_text = tokenizer.encode(text, return_tensors="pt", truncation=False).to(device)
    # Calculate overlap size
    max_tokens = 1024
    overlap_size = int(max_tokens * overlap_percentage / 100)

    # Generate summaries with overlapping chunks
    summaries = []
    if tokenized_text.size(1) - max_tokens+1 < 0:
        summary_ids = model.generate(tokenized_text[:,:], min_length=min_summary_length, max_length=max_summary_length, num_beams=16, early_stopping=True, length_penalty=0.8, repetition_penalty=1.5)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)
    else:
        for i in range(0, tokenized_text.size(1) - max_tokens + 1, max_tokens - overlap_size):
            start = i
            end = min(i + max_tokens, tokenized_text.size(1))
            chunk = tokenized_text[:, start:end]
            summary_ids = model.generate(chunk, min_length=min_summary_length, max_length=max_summary_length, num_beams=16, early_stopping=True, length_penalty=0.8, repetition_penalty=1.5)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary)

    # Concatenate summaries to create the final summary
    final_summary = " ".join(summaries)
    final_summary = final_summary.replace("\n"," ")
    return fix_grammar(final_summary)

def generate_pdf(summary,paper_name):
    pdf_file = "./temp/Summary.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)

    story = []

    # Adding Title to story
    titleStyle = getSampleStyleSheet()
    titleStyle = titleStyle['Title']
    title = Paragraph("Summary : "+paper_name, titleStyle)
    story.append(title)
    story.append(Spacer(1, 12))

    # Adding Summary
    paragraphStyle = getSampleStyleSheet()
    paragraphStyle = paragraphStyle["Normal"]
    paragraph = Paragraph(summary, paragraphStyle)
    story.append(paragraph)
    story.append(Spacer(1, 24))

    document.build(story)

def download_summary(file_path, filename):
    with open(file_path, "rb") as file:
        pdf_data = file.read()
    
    pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="{filename}">Download PDF File</a>'
    return href
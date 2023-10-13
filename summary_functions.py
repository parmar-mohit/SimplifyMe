import fitz
import re
from transformers import AutoTokenizer, BartForConditionalGeneration

def getSections(pdf_file_path):
    pdf_document = fitz.open(pdf_file_path)

    section_start_keywords = ["Abstract— ","INTRODUCTION","RELATED WORK","LITERATURE REVIEW", "METHODOLOGY","METHODOLOGIES", "RESULTS", "DATASET","EVALUTAION METRICS","DISCUSSIONS", "CONCLUSION", "REFERENCES"]

    # Define a regular expression pattern to match section titles
    section_pattern = "|".join(section_start_keywords)
    section_pattern = f"\\b({section_pattern})\\b"

    section_texts = []
    text = ""

    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        text += page.get_text()

    sections = re.split(section_pattern, text)
    for section_title, section_content in zip(sections[1::2],sections[2::2]):
        # Normalize section title
        section_title = section_title.strip().replace("\n", " ")
        section_content = section_content.strip() # removing extra whitespaces
        section_content = section_content.replace("\n"," ") # replacing line endings with spaces
        section_content = re.sub(r'\[\d+\]', '', section_content)
        section_texts.append( (section_title,section_content) )

    # Close the PDF file
    pdf_document.close()

    return section_texts

def getSummary(text):
    # Generating Tokens
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    input_tokens = tokenizer.encode(text, return_tensors="pt",max_length=1024,padding="max_length",truncation=True)
    
    # Generating Summaries
    model = BartForConditionalGeneration.from_pretrained("bart-papers-trained-model")
    summary_tokens = model.generate(input_tokens, min_length=64,max_length=256, num_beams=4, length_penalty=2.0,early_stopping=False)
    summary = tokenizer.decode(summary_tokens[0], skip_special_tokens=True)

    return summary
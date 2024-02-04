import fitz
import re
import streamlit as st
from transformers import AutoTokenizer, BartForConditionalGeneration

def getPaperContent(pdf_file_path):
    if pdf_file_path is None:
        st.error("Please upload a valid PDF file.")
        return []

    try:
        st.write("Opening PDF file...")
        pdf_document = fitz.open(pdf_file_path)
    except FileNotFoundError:
        st.error(f"File not found: {pdf_file_path}")
        return ""
    
    text = ""
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text += page.get_text()

    return text

def getSections(pdf_file_path):
    if pdf_file_path is None:
        st.error("Please upload a valid PDF file.")
        return []

    try:
        st.write("Opening PDF file...")
        pdf_document = fitz.open(pdf_file_path)
    except FileNotFoundError:
        st.error(f"File not found: {pdf_file_path}")
        return []

    section_start_keywords = ["Abstract— ", "INTRODUCTION", "RELATED WORK", "LITERATURE REVIEW", "METHODOLOGY",
                              "METHODOLOGIES", "RESULTS", "DATASET", "EVALUATION METRICS", "DISCUSSIONS", "CONCLUSION", "REFERENCES"]

    # Define a regular expression pattern to match section titles
    section_pattern = "|".join(section_start_keywords)
    section_pattern = f"\\b({section_pattern})\\b"

    section_texts = []
    text = ""

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text += page.get_text()

    sections = re.split(section_pattern, text)
    for section_title, section_content in zip(sections[1::2], sections[2::2]):
        # Normalize section title
        if section_title == "REFERENCES":
            continue
        section_title = section_title.strip().replace("\n", " ")
        section_content = section_content.strip()  # removing extra whitespaces
        section_content = section_content.replace("\n", " ")  # replacing line endings with spaces
        section_content = re.sub(r'\[\d+\]', '', section_content)
        section_texts.append((section_title, section_content))

    # Close the PDF file
    pdf_document.close()

    return section_texts

def getSummary(text):
    # Generating Tokens
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    input_tokens = tokenizer.encode(text, return_tensors="pt",max_length=1024,padding="max_length",truncation=False)
    
    print("Length of Input Tokens : ",len(input_tokens),type(input_tokens))
    
    # Generating Summaries
    model = BartForConditionalGeneration.from_pretrained("bart-papers-trained-model")

    summary_text = ""
    max_tokens = 1000
    for i in range(0,len(input_tokens),max_tokens):
        summary_tokens = model.generate(input_tokens[i:i+max_tokens], min_length=64,max_length=256, num_beams=4, length_penalty=2.0,early_stopping=False)
        summary_text += tokenizer.decode(summary_tokens[0], skip_special_tokens=True)

    return summary_text

def getSummaryWordLimit(text, word_limit):
    # Generating Tokens
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    input_tokens = tokenizer.encode(text, return_tensors="pt",max_length=1024,padding="max_length",truncation=False)
    
    # Generating Summaries
    model = BartForConditionalGeneration.from_pretrained("bart-papers-trained-model")
    input_tokens_length = len(input_tokens)
    max_tokens = 1024

    summary_text = ""
    if input_tokens_length > max_tokens:
        min_per_section = int( word_limit[0] / ( input_tokens_length // max_tokens ) )
        max_per_section = int( word_limit[1] / ( input_tokens_length // max_tokens) )
        
        for i in range(0,input_tokens_length,max_tokens):
            summary_tokens = model.generate(input_tokens[i:i+max_tokens], min_length=min_per_section,max_length=max_per_section, num_beams=4, length_penalty=2.0,early_stopping=False)
            summary_text += tokenizer.decode(summary_tokens[0], skip_special_tokens=True)
    else:
        summary_tokens = model.generate(input_tokens, min_length=64,max_length=256, num_beams=4, length_penalty=2.0,early_stopping=False)
        summary_text += tokenizer.decode(summary_tokens[0], skip_special_tokens=True)

    return summary_text
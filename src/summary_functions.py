import os
from transformers import AutoTokenizer, BartForConditionalGeneration
import spacy
from spacy.lang.en.examples import sentences

def getSummary(text):
    # Generating Tokens
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    input_tokens = tokenizer.encode(text, return_tensors="pt",max_length=1024,padding="max_length",truncation=True)
    
    # Generating Summaries
    model = BartForConditionalGeneration.from_pretrained('iter_trained_model')
    summary_tokens = model.generate(input_tokens, min_length=64,max_length=500, num_beams=15, length_penalty=2.0,early_stopping=False)
    summary = tokenizer.decode(summary_tokens[0], skip_special_tokens=True)

    return summary



# nlp = spacy.load("en_core_web_sm")

def remove_incomplete_sentences(summary):
    # Tokenize the summary using spaCy
    doc = nlp(summary)

    # Remove incomplete sentences
    complete_sentences = [sent.text for sent in doc.sents if sent.text.endswith('.')]

    # Rejoin the complete sentences
    complete_summary = ' '.join(complete_sentences)

    return complete_summary


import streamlit as st
import os
from functions import get_paper_content, generate_summary_paper, generate_summary_text, generate_pdf, download_summary, preprocess_text, fix_grammar

def app():
    # Set Streamlit app to use the full available width
    st.set_page_config(layout="wide")  
    st.title("SimplifyMe - A Content Summarizer")

    # Sidebar options
    st.sidebar.image('./Images/Logo.png')
    selected_option = st.sidebar.radio("Select Option", ["Research Paper", "Text", "Books"])
    
    if selected_option == "Research Paper":
        st.header("Summarize Research Paper")
        uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])
    
        if uploaded_file:
            paper_name = uploaded_file.name
            temp_file_path = save_uploaded_file(uploaded_file)
            st.success("File uploaded successfully")
            
            # Clean and summarize the PDF
            if st.button("Generate Summary"):
                with st.spinner("Processing..."):
                    paper_content = get_paper_content(temp_file_path)
                    summary = generate_summary_paper(paper_content)
                    st.subheader("Summary : " + paper_name )
                    st.markdown(f'<div style="text-align: justify">{summary}</div>', unsafe_allow_html=True)\
                    
                    #Generating and storing pdf
                    generate_pdf(summary,paper_name)
                    st.markdown(download_summary("./temp/Summary.pdf", f'{uploaded_file.name}_Summary.pdf'), unsafe_allow_html=True)
    elif selected_option == "Text":
        st.header("Summarize Text")
        summary_input = st.text_area("Enter your text for summarization")
        max_length = st.slider("Select Maximum Summary Length", min_value=30, max_value=500, value=150)
        min_length = st.slider("Select Minimum Summary Length", min_value=10, max_value=200, value=50)

        if st.button("Generate Summary"):
            if summary_input:
                # Summarize the user input with user-defined max_length and min_length
                cleaned_text = preprocess_text(summary_input)
                summary = generate_summary_text(cleaned_text, min_summary_length=min_length, max_summary_length=max_length)
                st.markdown(f'<div style="text-align: justify">{summary}</div>', unsafe_allow_html=True)
    elif selected_option == "Books":
        st.write("Coming Soon!....")

# Helper function to save uploaded file to a temporary file
def save_uploaded_file(uploaded_file):
    temp_dir = "./temp/"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)

    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.read())

    return temp_file_path

# Run the app
if __name__ == '__main__':
    app()

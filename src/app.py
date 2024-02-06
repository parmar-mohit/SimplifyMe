import streamlit as st
import os
from functions import generate_summary, get_paper_content, generate_pdf, download_summary

def app():
    # Set Streamlit app to use the full available width
    st.set_page_config(layout="wide")  
    st.title("SimplifyMe - Content Summarizer")

    # Sidebar options
    selected_option = st.sidebar.radio("Select Option", ["Research Paper", "Sections", "Books"])

    if selected_option == "Research Paper":
        st.header("Summarize Research Paper")
        uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])

        if uploaded_file:            
            # Save the uploaded file to a temporary file
            with st.spinner("Processing..."):
                temp_file_path = save_uploaded_file(uploaded_file)

            # Generate Summary of Paper
            if st.button("Generate Summary"):
                summary_result = generate_summary(get_paper_content(temp_file_path))

                if summary_result:
                    st.subheader(f"Summary")
                    st.markdown(f'<div style="text-align: justify">{summary_result}</div>', unsafe_allow_html=True)
                    generate_pdf(summary_result)
                    download_summary("./temp/Summary.pdf", f'{uploaded_file.name}_Summary.pdf')
                    # if st.button('Download Summary'):
                    #     print("Reached Here")
                    #     generate_pdf(summary_result)
                    #     st.markdown(download_summary(".temp/Summary.pdf", f'{uploaded_file.filename}_Summary.pdf'), unsafe_allow_html=True)
                else:
                    st.warning("Summary could not be generated for this section.")  
    elif selected_option == "Sections":
        st.header("Summarize Text")
        summary_input = st.text_area("Enter your text for summarization")
        max_length = st.slider("Select Maximum Summary Length", min_value=30, max_value=500, value=150)
        min_length = st.slider("Select Minimum Summary Length", min_value=10, max_value=200, value=50)

        if st.button("Generate Summary"):
            if summary_input:
                # Summarize the user input with user-defined max_length and min_length
                summary = generate_summary(summary_input,min_length,max_length)
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

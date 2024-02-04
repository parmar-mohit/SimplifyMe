import streamlit as st
import os
from functions import getSections, getSummary, getSummaryWordLimit, getPaperContent

def app():
    st.title("SimplifyMe - Content Summarizer")

    # Sidebar options
    selected_option = st.sidebar.radio("Select Option", ["Research Paper", "Text", "Books"])

    if selected_option == "Text":
        st.header("Summarize Text")
        summary_input = st.text_area("Enter your text for summarization")
        max_length = st.slider("Select Maximum Summary Length", min_value=30, max_value=500, value=150)
        min_length = st.slider("Select Minimum Summary Length", min_value=10, max_value=200, value=50)

        if st.button("Generate Summary"):
            if summary_input:
                # Summarize the user input with user-defined max_length and min_length
                summary = getSummaryWordLimit(summary_input,(min_length,max_length))
                st.success("Summary:\n" + summary)
    elif selected_option == "Research Paper":
        st.header("Summarize Research Paper")
        uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])

        if uploaded_file:
            st.write("Uploaded File Information:")
            
            # Save the uploaded file to a temporary file
            with st.spinner("Processing..."):
                temp_file_path = save_uploaded_file(uploaded_file)

            # Process the PDF file
            sections = getSections(temp_file_path)

            # Generate Summary for Entire Paper
            st.subheader("Entire Paper")
            if st.button(f"Generate Summary for Entire Paper"):
                summary_result = getSummary(getPaperContent(temp_file_path))

                if summary_result:
                    # Display section-wise summary
                    st.subheader(f"Summary for Entire Paper")
                    st.write(summary_result)
                else:
                    st.warning("Summary could not be generated for this section.")


            if len(sections) > 0:
                st.write("Extracted Sections:")
            else:
                st.write("No Sections Could be extracted")
            # Display extracted sections and generate summaries
            for section_title, section_content in sections:
                st.subheader(section_title)
                # st.write(section_content)

                # Add a "Generate" button for each section
                if st.button(f"Generate Summary for {section_title}"):
                    # Generate summary for each section
                    summary_result = getSummary(section_content)

                    if summary_result:
                        # Display section-wise summary
                        st.subheader(f"Summary for {section_title}")
                        st.write(summary_result)
                    else:
                        st.warning("Summary could not be generated for this section.")
        
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

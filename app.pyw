import tkinter as tk
from summary_functions import getSections, getSummary
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer
from tkinter import messagebox

def select_file_button_on_click():
    file_path = filedialog.askopenfilename(type=[("PDF",".pdf")])
    
    if not file_path:
        return

    welcome_label.config(text="Generating Summary.....")
    sections = getSections(file_path)
    pdf_file = "Summary.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)

    story = []

    for section in sections:
        if section[0] != "REFERENCES":
            welcome_label.config(text="Generating Summary for {}".format(section[0]))
            print("Generating Summary for {}".format(section[0]))

            # Testing Code
            fout = open("./temp/{}.txt".format(section[0]),"w",encoding="utf8")
            fout.write(section[1])
            fout.close()


            # Adding Title to story
            titleStyle = getSampleStyleSheet()
            titleStyle = titleStyle['Title']
            title = Paragraph(section[0], titleStyle)
            story.append(title)
            story.append(Spacer(1, 12))

            section_summary = getSummary(section[1])
            paragraphStyle = getSampleStyleSheet()
            paragraphStyle = paragraphStyle["Normal"]
            paragraph = Paragraph(section_summary, paragraphStyle)
            story.append(paragraph)
            story.append(Spacer(1, 24))

            print("Summary Generated for {}".format(section[0]))

    document.build(story)

    messagebox.showinfo("Summary Info","Summary has been sucessfully Generated")

    welcome_label.config(text=welcome_text)
    

root = tk.Tk()
root.title("SimplifyMe")
root.geometry("680x200")
root.configure(bg="#44f2bb")

welcome_text = "Welcome to SimplifyMe.\nWe generate concise research paper summaries for you that helps you save time"
welcome_label = tk.Label(text=welcome_text,justify="center",font=("Times New Roman",16),bg="#44f2bb",fg="#5a00c2")
select_file_button = tk.Button(text="Select Paper",justify="center",font=("Times New Roman",16),command=select_file_button_on_click,fg="#5a00c2",bg="#CCCCCC")

welcome_label.grid(row=0,column=0,padx=5,pady=5)
select_file_button.grid(row=1,column=0,padx=5,pady=5)

root.mainloop()
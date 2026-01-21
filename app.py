import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
import os

# --- Page Config ---
st.set_page_config(page_title="PDF Editor", layout="wide")
st.title("📄 Hindi-English PDF Editor (Web Version)")

# --- Sidebar Menu ---
menu = ["PDF Banayein", "PDF to Word", "PDF Merge"]
choice = st.sidebar.selectbox("Menu", menu)

# --- 1. PDF Banayein ---
if choice == "PDF Banayein":
    st.subheader("Naya PDF Likhein")
    text_input = st.text_area("Yahan text likhein", height=200)
    
    font_file = st.file_uploader("Hindi Font Upload Karein (.ttf)", type=['ttf'])
    
    if st.button("Download PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if font_file:
            with open("temp_font.ttf", "wb") as f:
                f.write(font_file.read())
            pdf.add_font('Custom', '', 'temp_font.ttf')
            pdf.set_font('Custom', size=14)
        else:
            pdf.set_font("Arial", size=12)
            
        pdf.multi_cell(0, 10, txt=text_input)
        pdf.output("output.pdf")
        
        with open("output.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="MyDoc.pdf")

# --- 2. PDF to Word ---
elif choice == "PDF to Word":
    st.subheader("PDF se Word Converter")
    pdf_file = st.file_uploader("PDF Upload", type=['pdf'])
    if pdf_file and st.button("Convert"):
        with open("temp_input.pdf", "wb") as f:
            f.write(pdf_file.read())
        cv = Converter("temp_input.pdf")
        cv.convert("output.docx")
        cv.close()
        with open("output.docx", "rb") as f:
            st.download_button("Download Word", f, file_name="converted.docx")

# --- 3. PDF Merge ---
elif choice == "PDF Merge":
    st.subheader("Merge PDFs")
    files = st.file_uploader("Files Select Karein", type=['pdf'], accept_multiple_files=True)
    if files and st.button("Merge"):
        merger = PdfWriter()
        for pdf in files:
            merger.append(pdf)
        merger.write("merged.pdf")
        merger.close()
        with open("merged.pdf", "rb") as f:
            st.download_button("Download Merged PDF", f, file_name="merged.pdf")

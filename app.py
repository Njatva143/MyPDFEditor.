import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from PIL import Image
import pytesseract
import os

# --- Page Config ---
st.set_page_config(page_title="Universal PDF Tool", layout="wide")
st.title("📄 All-in-One Hindi-English PDF Editor & Converter")

# --- Sidebar Menu ---
menu = ["PDF Banayein (Hindi/English/Typewriter)", "PDF se Word (Convert)", "OCR (Image/PDF to Text)", "PDF Merge Karein"]
choice = st.sidebar.selectbox("Kya kaam karna hai?", menu)

# --- FEATURE 1: PDF BANAYEIN (With Custom Font & Typewriter Look) ---
if choice == "PDF Banayein (Hindi/English/Typewriter)":
    st.header("📝 Naya PDF Taiyar Karein")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        user_text = st.text_area("Yahan apna text likhein (Unicode Hindi ya English):", height=300)
    
    with col2:
        st.subheader("Settings")
        font_file = st.file_uploader("Font Upload Karein (.ttf)", type=['ttf'], help="Hindi ke liye 'Mangal' ya Typewriter ke liye 'Kruti Dev' upload karein")
        font_size = st.slider("Font Size", 10, 30, 14)
        line_spacing = st.slider("Line Spacing", 5, 15, 10)
        
        is_typewriter = st.checkbox("Typewriter Look (Courier default agar font na ho)")

    if st.button("Download PDF"):
        if user_text:
            pdf = FPDF()
            pdf.add_page()
            
            # Font Handling
            if font_file:
                with open("temp_font.ttf", "wb") as f:
                    f.write(font_file.read())
                pdf.add_font('CustomFont', '', 'temp_font.ttf')
                pdf.set_font('CustomFont', size=font_size)
            elif is_typewriter:
                pdf.set_font("Courier", size=font_size)
            else:
                pdf.set_font("Arial", size=font_size)

            # Rendering Text
            pdf.multi_cell(0, line_spacing, txt=user_text)
            pdf.output("output_doc.pdf")
            
            with open("output_doc.pdf", "rb") as f:
                st.download_button("📥 PDF Download Karein", f, file_name="MeraDocument.pdf")
        else:
            st.error("Kripya kuch text likhein!")

# --- FEATURE 2: PDF SE WORD ---
elif choice == "PDF se Word (Convert)":
    st.header("🔃 PDF ko Word (.docx) mein badlein")
    uploaded_file = st.file_uploader("PDF File Upload Karein", type=['pdf'])
    
    if uploaded_file and st.button("Word mein badlein"):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        
        docx_file = "converted.docx"
        cv = Converter("temp.pdf")
        cv.convert(docx_file)
        cv.close()
        
        with open(docx_file, "rb") as f:
            st.download_button("📥 Word File Download", f, file_name="converted_file.docx")

# --- FEATURE 3: OCR (Image/PDF to Text) ---
elif choice == "OCR (Image/PDF to Text)":
    st.header("🔍 Photo se Text Nikalein (Hindi/English)")
    st.info("Iske liye aapke system mein Tesseract OCR install hona chahiye.")
    
    ocr_file = st.file_uploader("Image ya PDF upload karein", type=['png', 'jpg', 'jpeg', 'pdf'])
    lang = st.selectbox("Language Chunein", ["eng", "hin", "eng+hin"])

    if ocr_file and st.button("Text Extract Karein"):
        img = Image.open(ocr_file)
        # OCR Logic
        text = pytesseract.image_to_string(img, lang=lang)
        st.subheader("Nikala gaya Text:")
        st.text_area("Result:", text, height=250)
        st.download_button("📥 Text File Download", text, file_name="extracted.txt")

# --- FEATURE 4: PDF MERGE ---
elif choice == "PDF Merge Karein":
    st.header("📂 Kai PDF ko ek banayein")
    files = st.file_uploader("Files Select Karein", type=['pdf'], accept_multiple_files=True)
    
    if files and st.button("Merge PDFs"):
        merger = PdfWriter()
        for pdf_file in files:
            merger.append(pdf_file)
        
        merger.write("merged.pdf")
        merger.close()
        
        with open("merged.pdf", "rb") as f:
            st.download_button("📥 Merged PDF Download", f, file_name="final_merged.pdf")

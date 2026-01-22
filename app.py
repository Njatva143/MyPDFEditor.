import streamlit as st
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pytesseract
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Correct Hindi Editor", layout="wide")
st.title("📄 Hindi PDF Editor (No Spelling Mistakes)")

# --- FONT FILES ---
# GitHub par ye 2 files honi chahiye:
# 1. Hindi.ttf (Normal look ke liye - Hind/Mangal)
# 2. Legal.ttf (Typewriter look ke liye - Noto Serif Devanagari)

hindi_font = "Hindi.ttf"
legal_font = "Legal.ttf"

# --- MAIN INTERFACE ---
st.header("✏️ Error-Free Hindi Editor")

# Upload
uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'], key="main_upl")

extracted_text = ""
if uploaded_file:
    use_ocr = st.toggle("OCR Mode (Text Scan)", value=True)
    if use_ocr:
        with st.spinner("Scanning..."):
            try:
                images = convert_from_bytes(uploaded_file.read())
                for img in images:
                    extracted_text += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
            except: pass

# --- EDITOR ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Editor (Sahi Hindi Likhein)")
    # User yahan normal mobile hindi likhega
    user_text = st.text_area("Content:", value=extracted_text, height=500)

with col2:
    st.subheader("Print Settings")
    
    # STYLE SELECTION
    style = st.radio("Style Chunein:", 
                     ["Modern (Normal)", 
                      "Legal/Court Style (Best for Documents)", 
                      "English"])
    
    font_size = st.slider("Font Size", 10, 30, 14)
    line_gap = st.slider("Line Gap", 5, 15, 8)
    
    if st.button("Generate Final PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- FONT LOGIC (NO CONVERSION NEEDED) ---
        font_ready = False
        
        # 1. LEGAL STYLE (Ye typewriter jaisa dikhega lekin spelling sahi rahegi)
        if style == "Legal/Court Style (Best for Documents)":
            if os.path.exists(legal_font):
                pdf.add_font("LegalF", "", legal_font)
                pdf.set_font("LegalF", size=font_size)
                font_ready = True
            else:
                st.error("❌ 'Legal.ttf' file nahi mili! Please GitHub check karein.")

        # 2. MODERN STYLE
        elif style == "Modern (Normal)":
            if os.path.exists(hindi_font):
                pdf.add_font("ModernF", "", hindi_font)
                pdf.set_font("ModernF", size=font_size)
                font_ready = True
            else:
                st.error("❌ 'Hindi.ttf' file nahi mili!")
        
        # 3. ENGLISH
        else:
            pdf.set_font("Arial", size=font_size)
            font_ready = True

        # --- SAVE ---
        if font_ready:
            try:
                # Direct text print karein (Kyunki ab font Unicode compatible hai)
                pdf.multi_cell(0, line_gap, txt=user_text)
                pdf.output("final_output.pdf")
                with open("final_output.pdf", "rb") as f:
                    st.success("✅ PDF Taiyar Hai! (Spelling Check Karein)")
                    st.download_button("📥 Download PDF", f, file_name="Sahi_Hindi_Doc.pdf")
            except Exception as e:
                st.error(f"Error: {e}")
                

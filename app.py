import streamlit as st
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pytesseract
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Hindi PDF Extractor", layout="wide")
st.title("📄 Hindi PDF Editor (OCR Force Mode)")

# --- FONT SETUP ---
fonts = {
    "Hindi": "Hindi.ttf",           
    "Typewriter": "Typewriter.ttf" 
}

# --- MAIN LOGIC ---
st.header("✏️ Hindi PDF Edit Karein")

uploaded_file = st.file_uploader("Hindi PDF Upload Karein", type=['pdf'], key="ocr_upload")

if uploaded_file:
    # Status bar dikhayenge taaki user ko lage kaam ho raha hai
    with st.spinner("Hindi Text Scan ho raha hai... (Kripya wait karein)"):
        try:
            # 1. PDF ko Images mein badalna
            images = convert_from_bytes(uploaded_file.read())
            
            extracted_text = ""
            
            # 2. Har image se Hindi Text nikalna
            for i, img in enumerate(images):
                # 'hin+eng' ka matlab hai Hindi aur English dono padho
                text = pytesseract.image_to_string(img, lang='hin+eng')
                extracted_text += text + "\n"
                
        except Exception as e:
            st.error(f"Error: {e}. (Kya aapne packages.txt banayi hai?)")
            extracted_text = ""

    # --- EDITOR BOX ---
    if extracted_text:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success("✅ Text mil gaya!")
            # Yahan text dikhega aur edit hoga
            final_text = st.text_area("Yahan Edit Karein:", value=extracted_text, height=600)
            
        with col2:
            st.subheader("Download Settings")
            font_choice = st.radio("Font Style:", ["Hindi (Mangal)", "Typewriter", "English"])
            font_size = st.slider("Size:", 10, 30, 14)
            
            if st.button("Save PDF"):
                pdf = FPDF()
                pdf.add_page()
                
                # --- FONT LOGIC ---
                pdf.set_font("Arial", size=12) # Safety Default
                
                if font_choice == "Hindi (Mangal)" and os.path.exists(fonts["Hindi"]):
                    pdf.add_font("H", "", fonts["Hindi"])
                    pdf.set_font("H", size=font_size)
                elif font_choice == "Typewriter" and os.path.exists(fonts["Typewriter"]):
                    pdf.add_font("T", "", fonts["Typewriter"])
                    pdf.set_font("T", size=font_size)
                
                pdf.multi_cell(0, 10, final_text)
                pdf.output("final.pdf")
                with open("final.pdf", "rb") as f:
                    st.download_button("Download Now", f, file_name="edited.pdf")
    else:
        st.warning("⚠️ Text extract nahi hua. Shayad 'packages.txt' missing hai ya PDF blank hai.")
        

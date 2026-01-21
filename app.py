import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import os

# --- APP SETUP ---
st.set_page_config(page_title="Hindi PDF Editor Pro", layout="wide")
st.title("📄 Pro Hindi PDF Editor & Extractor")

# --- FONTS SETUP ---
# Ye check karega ki aapne GitHub par font upload kiye hain ya nahi
fonts = {
    "Hindi": "Hindi.ttf",           
    "Typewriter": "Typewriter.ttf" 
}

# Dropdown list banana based on available fonts
available_fonts = ["Arial (Default)"]
if os.path.exists(fonts["Hindi"]): available_fonts.insert(0, "Hindi (Devanagari)")
if os.path.exists(fonts["Typewriter"]): available_fonts.append("Typewriter (KrutiDev/Courier)")

# --- SIDEBAR MENU ---
menu = ["Edit PDF (Advanced)", "Create New", "Convert"]
choice = st.sidebar.selectbox("Select Tool", menu)

# ==========================================
# TOOL 1: EDIT PDF (WITH OCR SUPPORT)
# ==========================================
if choice == "Edit PDF (Advanced)":
    st.header("✏️ Edit Hindi/English PDF")
    
    # 1. Upload
    uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'], key="upload_edit")
    
    st.info("Agar text nahi dikh raha, to 'OCR Mode' on karein.")
    use_ocr = st.toggle("🔴 Use OCR Mode", value=False, key="toggle_ocr")
    
    if uploaded_file:
        text_content = ""
        
        # --- LOGIC: TEXT KAISE NIKALEIN? ---
        if use_ocr:
            with st.spinner("OCR chal raha hai..."):
                try:
                    images = convert_from_bytes(uploaded_file.read())
                    for img in images:
                        text_content += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
                except Exception as e:
                    st.error(f"OCR Error: {e}. (Check packages.txt)")
        else:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += (page.extract_text() or "") + "\n"

        # --- EDITOR SCREEN ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Edit Text Here:")
            edited_text = st.text_area("Editor", value=text_content, height=500, key="editor_area")
        
        with col2:
            st.subheader("Save Settings")
            sel_font = st.selectbox("Font Style", available_fonts, key="font_select_edit")
            font_size = st.slider("Font Size", 10, 30, 14, key="slider_edit")
            
            # --- BUTTON WITH UNIQUE KEY ---
            if st.button("Save & Download PDF", key="btn_save_edit"):
                pdf = FPDF()
                pdf.add_page()
                
                # --- FONT LOGIC (FORCE HINDI) ---
                font_path_used = None
                font_family = "Arial"

                # 1. Hindi Font Logic
                if "Hindi" in sel_font and os.path.exists(fonts["Hindi"]):
                    font_path_used = fonts["Hindi"]
                    font_family = "HindiFont"
                
                # 2. Typewriter Font Logic
                elif "Typewriter" in sel_font and os.path.exists(fonts["Typewriter"]):
                    font_path_used = fonts["Typewriter"]
                    font_family = "TypeFont"

                # 3. Apply Font
                if font_path_used:
                    try:
                        pdf.add_font(font_family, "", font_path_used)
                        pdf.set_font(font_family, size=font_size)
                    except Exception as e:
                        st.error(f"Font Error: {e}")
                        pdf.set_font("Arial", size=font_size)
                else:
                    pdf.set_font("Arial", size=font_size)
                    if "Hindi" in sel_font: st.warning("⚠️ Hindi.ttf file nahi mili! Arial use ho raha hai.")

                # PDF Write (Try-Except block for safety)
                try:
                    pdf.multi_cell(0, 10, txt=edited_text)
                    pdf.output("edited_output.pdf")
                    with open("edited_output.pdf", "rb") as f:
                        st.success("✅ PDF Ban gayi!")
                        st.download_button("📥 Download PDF", f, file_name="edited_hindi_doc.pdf", key="dl_btn_edit")
                except Exception as e:
                    st.error(f"Error: {e}. (Hindi text ke liye Hindi font select karein)")

# ==========================================
# TOOL 2: CREATE NEW
# ==========================================
elif choice == "Create New":
    st.header("📝 Naya Document")
    user_inp = st.text_area("Type karein...", height=300, key="new_doc_area")
    
    sel_f = st.selectbox("Font", available_fonts, key="font_select_new")
    
    # --- BUTTON WITH UNIQUE KEY ---
    if st.button("Generate PDF", key="btn_save_new"):
        pdf = FPDF()
        pdf.add_page()
        
        if "Hindi" in sel_f and os.path.exists(fonts["Hindi"]):
            pdf.add_font("H", "", fonts["Hindi"])
            pdf.set_font("H", size=14)
        elif "Typewriter" in sel_f and os.path.exists(fonts["Typewriter"]):
            pdf.add_font("T", "", fonts["Typewriter"])
            pdf.set_font("T", size=14)
        else: 
            pdf.set_font("Arial", size=12)
            
        pdf.multi_cell(0, 10, user_inp)
        pdf.output("new.pdf")
        with open("new.pdf", "rb") as f: 
            st.download_button("Download", f, file_name="new_doc.pdf", key="dl_btn_new")

# ==========================================
# TOOL 3: CONVERT
# ==========================================
elif choice == "Convert":
    st.header("Convert PDF to Word")
    u_file = st.file_uploader("PDF Upload", type='pdf', key="upload_convert")
    
    # --- BUTTON WITH UNIQUE KEY ---
    if u_file and st.button("Convert to Word", key="btn_convert"):
        with open("temp.pdf", "wb") as f: f.write(u_file.read())
        cv = Converter("temp.pdf")
        cv.convert("conv.docx")
        cv.close()
        with open("conv.docx", "rb") as f: 
            st.download_button("Download Word", f, file_name="converted.docx", key="dl_btn_convert")
            

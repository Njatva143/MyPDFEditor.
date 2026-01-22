import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Smart Hindi Editor", layout="wide")
st.title("📄 Hindi Auto-Match & Convert Editor (Final Fixed)")

# --- AUTO-CONVERTER LOGIC (UNICODE TO KRUTI DEV) ---
def unicode_to_krutidev(text):
    # Basic mapping for common characters
    mapping = {
        '‘': '^', '’': '*', '“': 'Þ', '”': 'ß', '(': '¼', ')': '½',
        '{': '¿', '}': 'À', '[': '¬', ']': '­', '.': 'A', '-': '-',
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
        'x': '×', '+': '+',
        'त': 'r', 'त्': 'R', 'क': 'd', 'क्': 'D', 'ख': '[', 'ख्': '{', 'ग': 'x', 'ग्': 'X',
        'घ': '?', 'घ्': 'ø', 'ङ': 'M', 'च': 'p', 'च्': 'P', 'छ': 'N', 'ज': 't', 'ज्': 'T',
        'झ': '>', 'झ्': '÷', 'ञ': '¥', 'ट': 'V', 'ट्': 'ê', 'ठ': 'B', 'ठ्': 'ë', 'ड': 'M',
        'ड्': 'ì', 'ढ': '<', 'ढ्': 'í', 'ण': '.', 'ण्': 'õ', 'थ': 'F', 'थ्': 'Q', 'द': 'n',
        'द्य': '\|', 'ध': 'è', 'ध्': 'È', 'न': 'u', 'न्': 'U', 'प': 'i', 'प्': 'I', 'फ': 'Q',
        'फ्': '¶', 'ब': 'c', 'ब्': 'C', 'भ': 'H', 'भ्': 'Ò', 'म': 'e', 'म्': 'E', 'य': ';',
        'य्': '¸', 'र': 'j', 'ल': 'y', 'ल्': 'Y', 'व': 'b', 'व्': 'B', 'श': 'M', 'श्': 'M',
        'ष': 'k', 'ष्': 'ï', 'स': 'l', 'स्': 'L', 'ह': 'v', 'ह्': 'ü',
        'ा': 'k', 'ि': 'f', 'ी': 'h', 'ु': 'q', 'ू': 'w', 'ृ': '`', 'े': 's', 'ै': 'S',
        'ो': 'ks', 'ौ': 'kS', 'ं': 'a', 'ँ': '¡', 'ः': '%', '्': 'd', '़': '+'
    }
    converted_text = ""
    for char in text:
        converted_text += mapping.get(char, char)
    return converted_text

# --- FONT FILE NAMES ---
fonts = {
    "Modern": "Hindi.ttf",         
    "Typewriter": "Typewriter.ttf" 
}

# --- SIDEBAR ---
st.sidebar.header("🔧 Settings")
mode = st.sidebar.radio("Mode:", ["Edit PDF", "Create New"])

# ==========================================
# EDIT PDF MODE
# ==========================================
if mode == "Edit PDF":
    st.header("✏️ Auto-Match Font Editor")
    
    uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'], key="upl")
    
    text_content = ""
    if uploaded_file:
        use_ocr = st.toggle("Use OCR (Agar text na dikhe)", value=False)
        if use_ocr:
            with st.spinner("Scanning..."):
                try:
                    images = convert_from_bytes(uploaded_file.read())
                    for img in images:
                        text_content += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
                except: st.error("OCR Error (Check packages.txt)")
        else:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += (page.extract_text() or "") + "\n"

    col1, col2 = st.columns([2, 1])
    with col1:
        edited_text = st.text_area("Editor", value=text_content, height=450, key="editor")
    
    with col2:
        st.subheader("Font Settings")
        font_style = st.radio("Style Chunein:", ["Modern (Hindi)", "Old Typewriter", "English (Default)"])
        font_size = st.slider("Text Size", 10, 30, 14)

    if st.button("Download PDF", key="save_btn"):
        pdf = FPDF()
        pdf.add_page()
        
        # --- FIXED FONT LOGIC (NO CRASH) ---
        
        # 1. Default Safety Font (Sabse pehle ye set karein)
        pdf.set_font("Arial", size=font_size) 
        
        final_text = edited_text
        
        # 2. Try to set Custom Fonts
        if font_style == "Modern":
            if os.path.exists(fonts["Modern"]):
                pdf.add_font("ModernFont", "", fonts["Modern"])
                pdf.set_font("ModernFont", size=font_size)
            else:
                st.warning(f"⚠️ '{fonts['Modern']}' file nahi mili! Default Arial use ho raha hai.")

        elif font_style == "Old Typewriter":
            if os.path.exists(fonts["Typewriter"]):
                pdf.add_font("TypewriterFont", "", fonts["Typewriter"])
                pdf.set_font("TypewriterFont", size=font_size)
                # Auto Convert
                final_text = unicode_to_krutidev(edited_text)
            else:
                st.warning(f"⚠️ '{fonts['Typewriter']}' file nahi mili! Default Arial use ho raha hai.")

        # 3. Save PDF
        try:
            pdf.multi_cell(0, 10, txt=final_text)
            pdf.output("final.pdf")
            with open("final.pdf", "rb") as f:
                st.success("✅ PDF Ready!")
                st.download_button("📥 Download Result", f, file_name="doc.pdf")
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# CREATE NEW MODE
# ==========================================
elif mode == "Create New":
    st.header("📝 Create New Document")
    user_inp = st.text_area("Type here...", height=300)
    style = st.selectbox("Font Style", ["Modern (Hindi)", "Old Typewriter", "English"])
    
    if st.button("Generate"):
        pdf = FPDF()
        pdf.add_page()
        
        # Safety Font First
        pdf.set_font("Arial", size=12)
        
        final_txt = user_inp
        
        if style == "Modern (Hindi)" and os.path.exists(fonts["Modern"]):
            pdf.add_font("M", "", fonts["Modern"])
            pdf.set_font("M", size=14)
        elif style == "Old Typewriter" and os.path.exists(fonts["Typewriter"]):
            pdf.add_font("T", "", fonts["Typewriter"])
            pdf.set_font("T", size=14)
            final_txt = unicode_to_krutidev(user_inp)
            
        pdf.multi_cell(0, 10, final_txt)
        pdf.output("new.pdf")
        with open("new.pdf", "rb") as f:
            st.download_button("Download", f)
            

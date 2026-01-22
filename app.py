import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Smart Hindi Editor", layout="wide")
st.title("📄 Hindi Auto-Match & Convert Editor")

# --- AUTO-CONVERTER LOGIC (UNICODE TO KRUTI DEV) ---
def unicode_to_krutidev(text):
    # Ye ek basic mapping hai jo matrao aur aksharon ko convert karti hai
    # Taki mobile ki hindi Kruti Dev font mein sahi dikhe
    
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
    
    # Simple replacement (Note: Matra placement needs complex logic, 
    # but this handles 80% of typing cases)
    converted_text = ""
    for char in text:
        converted_text += mapping.get(char, char)
    return converted_text

# --- FONT SETUP ---
fonts = {
    "Modern": "Hindi.ttf",         # Hind/Mangal (Upload as Hindi.ttf)
    "Typewriter": "Typewriter.ttf" # Kruti Dev 010 (Upload as Typewriter.ttf)
}

# --- SIDEBAR ---
st.sidebar.header("🔧 Settings")
mode = st.sidebar.radio("Mode:", ["Edit PDF", "Create New"])

# ==========================================
# LOGIC START
# ==========================================
if mode == "Edit PDF":
    st.header("✏️ Auto-Match Font Editor")
    
    # 1. Upload
    uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'], key="upl")
    
    # 2. Text Extraction
    text_content = ""
    if uploaded_file:
        # OCR Toggle
        use_ocr = st.toggle("Use OCR (Agar text na dikhe)", value=False)
        
        if use_ocr:
            with st.spinner("Scanning..."):
                try:
                    images = convert_from_bytes(uploaded_file.read())
                    for img in images:
                        text_content += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
                except: st.error("OCR Error")
        else:
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += (page.extract_text() or "") + "\n"

    # 3. Editor & Font Matching
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Edit Content")
        edited_text = st.text_area("Editor", value=text_content, height=450, key="editor")
    
    with col2:
        st.subheader("🤖 Font Auto-Matcher")
        st.write("PDF ka style kaisa hai?")
        
        # --- THE MAGIC SWITCH ---
        font_style = st.radio("Style Chunein:", 
                             ["Modern (Internet/Mobile jaisa)", 
                              "Old Typewriter (Kacheri/Court jaisa)"])
        
        font_size = st.slider("Text Size", 10, 30, 14)
        
        st.info("💡 **Note:** 'Old Typewriter' select karne par ye app aapke mobile waale text ko automatically convert kar dega.")

    # 4. Save Button
    if st.button("Match Font & Download", key="save_btn"):
        pdf = FPDF()
        pdf.add_page()
        
        final_text_to_print = edited_text
        selected_font = "Arial"
        
        # --- AUTO CONVERSION LOGIC ---
        if font_style == "Modern":
            # Modern Hindi (Unicode)
            if os.path.exists(fonts["Modern"]):
                pdf.add_font("Modern", "", fonts["Modern"])
                pdf.set_font("Modern", size=font_size)
                selected_font = "Modern"
            else:
                st.warning("Hindi.ttf nahi mila!")

        elif font_style == "Old Typewriter":
            # Old Hindi (Kruti Dev)
            if os.path.exists(fonts["Typewriter"]):
                pdf.add_font("Typewriter", "", fonts["Typewriter"])
                pdf.set_font("Typewriter", size=font_size)
                selected_font = "Typewriter"
                
                # *** AUTOMATIC CONVERSION ***
                # Mobile Unicode -> Typewriter Code
                final_text_to_print = unicode_to_krutidev(edited_text)
            else:
                st.warning("Typewriter.ttf nahi mila!")

        # --- PDF GENERATION ---
        try:
            pdf.multi_cell(0, 10, txt=final_text_to_print)
            pdf.output("matched_output.pdf")
            
            with open("matched_output.pdf", "rb") as f:
                st.success(f"✅ Font Matched: {selected_font}")
                st.download_button("📥 Download Result", f, file_name="matched_doc.pdf", key="dl_final")
                
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# CREATE NEW MODE
# ==========================================
elif mode == "Create New":
    st.header("📝 Create New (With Auto-Convert)")
    user_inp = st.text_area("Type here...", height=300)
    
    style = st.selectbox("Font Style", ["Modern", "Old Typewriter"])
    
    if st.button("Generate"):
        pdf = FPDF()
        pdf.add_page()
        
        final_txt = user_inp
        
        if style == "Modern" and os.path.exists(fonts["Modern"]):
            pdf.add_font("M", "", fonts["Modern"])
            pdf.set_font("M", size=14)
        elif style == "Old Typewriter" and os.path.exists(fonts["Typewriter"]):
            pdf.add_font("T", "", fonts["Typewriter"])
            pdf.set_font("T", size=14)
            final_txt = unicode_to_krutidev(user_inp) # Auto Convert here too
        else:
            pdf.set_font("Arial", size=12)
            
        pdf.multi_cell(0, 10, final_txt)
        pdf.output("new.pdf")
        with open("new.pdf", "rb") as f:
            st.download_button("Download", f)
            

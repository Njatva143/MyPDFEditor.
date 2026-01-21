import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from PIL import Image
import pytesseract
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="Ultimate Doc Editor", layout="wide")
st.title("📄 All-in-One: Edit, Convert & Typewriter Tool")
st.markdown("""
<style>
.big-font { font-size:20px !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
menu = ["Edit Existing PDF (Edit Karein)", "Create New Document (Naya Banayein)", "PDF to Word (Convert)", "Image OCR (Photo se Text)"]
choice = st.sidebar.selectbox("Select Tool / Tool Chunein", menu)

# ==========================================
# TOOL 1: EDIT EXISTING PDF
# ==========================================
if choice == "Edit Existing PDF (Edit Karein)":
    st.header("✏️ Bani hui PDF ko Edit Karein")
    st.info("Step 1: PDF Upload karein -> Step 2: Text Edit karein -> Step 3: Font Chunein -> Step 4: Download karein")
    
    uploaded_file = st.file_uploader("PDF File Upload", type=['pdf'])
    
    if uploaded_file:
        # --- Text Extraction ---
        try:
            reader = PdfReader(uploaded_file)
            text_content = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content += extracted + "\n"
            
            if not text_content.strip():
                st.warning("⚠️ Is PDF se text nahi nikla. Shayad ye scanned image hai. Kripya 'Image OCR' tool use karein.")
            
            # --- Editing Area ---
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Text Editor")
                edited_text = st.text_area("Yahan badlav karein:", value=text_content, height=500)
            
            with col2:
                st.subheader("Font Settings")
                font_type = st.radio("Font Style Chunein:", ["Standard (English)", "Hindi (Mangal/Lohit)", "Typewriter (KrutiDev/Courier)"])
                
                custom_font = st.file_uploader("Upload .ttf Font (Zaroori hai)", type=['ttf'], help="Hindi ya Typewriter look ke liye font file upload karein.")
                
                font_size = st.slider("Font Size", 10, 30, 14)
                spacing = st.slider("Line Spacing", 5, 20, 8)

            # --- Save Logic ---
            if st.button("Save & Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                
                # Font Handling Logic
                if custom_font:
                    with open("temp_font.ttf", "wb") as f:
                        f.write(custom_font.read())
                    pdf.add_font('UserFont', '', 'temp_font.ttf')
                    pdf.set_font('UserFont', size=font_size)
                
                elif font_type == "Typewriter (KrutiDev/Courier)":
                    # Agar font upload nahi kiya toh default Courier use karega
                    pdf.set_font("Courier", size=font_size)
                
                else:
                    pdf.set_font("Arial", size=font_size)

                # Writing Text
                try:
                    pdf.multi_cell(0, spacing, txt=edited_text)
                    pdf.output("edited_doc.pdf")
                    
                    with open("edited_doc.pdf", "rb") as f:
                        st.success("✅ PDF Taiyar hai!")
                        st.download_button("📥 Download PDF", f, file_name="edited_document.pdf")
                except Exception as e:
                    st.error(f"Error: {e}. (Tip: Hindi text ke liye Font upload karna zaroori hai)")

        except Exception as e:
            st.error(f"Error reading PDF: {e}")

# ==========================================
# TOOL 2: CREATE NEW DOCUMENT
# ==========================================
elif choice == "Create New Document (Naya Banayein)":
    st.header("📝 Naya Document Banayein")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_area("Yahan type karein...", height=400)
    
    with col2:
        st.info("Settings")
        is_manual = st.checkbox("Manual Typewriter Mode")
        u_font = st.file_uploader("Custom Font (.ttf)", type=['ttf'])
        
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        
        if u_font:
            with open("temp_custom.ttf", "wb") as f:
                f.write(u_font.read())
            pdf.add_font('MyFont', '', 'temp_custom.ttf')
            pdf.set_font('MyFont', size=14)
        elif is_manual:
            pdf.set_font("Courier", size=14) # Default Typewriter Look
        else:
            pdf.set_font("Arial", size=12)
            
        pdf.multi_cell(0, 10, txt=user_input)
        pdf.output("new_doc.pdf")
        
        with open("new_doc.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name="new_creation.pdf")

# ==========================================
# TOOL 3: PDF TO WORD CONVERTER
# ==========================================
elif choice == "PDF to Word (Convert)":
    st.header("🔃 Convert PDF to Word")
    p_file = st.file_uploader("PDF File Upload", type=['pdf'])
    
    if p_file and st.button("Convert Now"):
        with open("temp_convert.pdf", "wb") as f:
            f.write(p_file.read())
        
        cv = Converter("temp_convert.pdf")
        cv.convert("final_word.docx")
        cv.close()
        
        with open("final_word.docx", "rb") as f:
            st.download_button("📥 Download Word File", f, file_name="converted.docx")

# ==========================================
# TOOL 4: OCR (IMAGE TO TEXT)
# ==========================================
elif choice == "Image OCR (Photo se Text)":
    st.header("📷 Photo/Scanned PDF se Text Nikalein")
    st.warning("Note: Is feature ke liye server par Tesseract install hona chahiye.")
    
    img_file = st.file_uploader("Image Upload Karein (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    lang_opt = st.selectbox("Language", ["English (eng)", "Hindi (hin)", "Mix (eng+hin)"])
    
    if img_file and st.button("Extract Text"):
        image = Image.open(img_file)
        # Simple extraction
        lang_code = "eng"
        if "Hindi" in lang_opt: lang_code = "hin"
        if "Mix" in lang_opt: lang_code = "eng+hin"
        
        try:
            text = pytesseract.image_to_string(image, lang=lang_code)
            st.text_area("Result:", value=text, height=300)
        except Exception as e:
            st.error("OCR Error. Shayad Tesseract installed nahi hai.")
            

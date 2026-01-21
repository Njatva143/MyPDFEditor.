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

# --- FONTS SETUP (GitHub se auto-load) ---
fonts = {
    "Hindi": "Hindi.ttf",           
    "Typewriter": "Typewriter.ttf" 
}
available_fonts = ["Arial (Default)"]
if os.path.exists(fonts["Hindi"]): available_fonts.insert(0, "Hindi (Devanagari)")
if os.path.exists(fonts["Typewriter"]): available_fonts.append("Typewriter (KrutiDev/Courier)")

# --- MENU ---
menu = ["Edit PDF (Advanced)", "Create New", "Convert"]
choice = st.sidebar.selectbox("Select Tool", menu)

# ==========================================
# TOOL 1: EDIT PDF (WITH OCR SUPPORT)
# ==========================================
if choice == "Edit PDF (Advanced)":
    st.header("✏️ Edit Hindi/English PDF")
    
    # 1. Upload
    uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'])
    
    # 2. Extraction Method Choice
    st.info("Agar normal mode mein Hindi text nahi dikh raha, to niche 'OCR Mode' on karein.")
    use_ocr = st.toggle("🔴 Use OCR Mode (Jab text na dikhe)", value=False)
    
    if uploaded_file:
        text_content = ""
        
        # --- LOGIC: TEXT KAISE NIKALEIN? ---
        if use_ocr:
            with st.spinner("OCR chal raha hai (thoda time lagega)..."):
                try:
                    # PDF ko images mein badalna
                    images = convert_from_bytes(uploaded_file.read())
                    for img in images:
                        # Hindi + English dono scan karega
                        text_content += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
                except Exception as e:
                    st.error(f"OCR Error: {e}. (Check packages.txt)")
        else:
            # Normal Extraction
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text_content += (page.extract_text() or "") + "\n"

        # --- EDITOR SCREEN ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Edit Text Here:")
            # Agar text khali hai to warning dega
            if not text_content.strip():
                st.warning("⚠️ Text nahi mila! Upar 'Use OCR Mode' button on karein.")
                
            edited_text = st.text_area("Editor", value=text_content, height=500)
        
        with col2:
            st.subheader("Save Settings")
            sel_font = st.selectbox("Font Style", available_fonts)
            font_size = st.slider("Font Size", 10, 30, 14)
            
            if st.button("Save & Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                
                # --- FONT SELECTION LOGIC ---
                # 1. Hindi Font
                if "Hindi" in sel_font and os.path.exists(fonts["Hindi"]):
                    pdf.add_font("HindiFont", "", fonts["Hindi"])
                    pdf.set_font("HindiFont", size=font_size)
                
                # 2. Typewriter Font
                elif "Typewriter" in sel_font and os.path.exists(fonts["Typewriter"]):
                    pdf.add_font("TypeFont", "", fonts["Typewriter"])
                    pdf.set_font("TypeFont", size=font_size)
                
                # 3. Default
                else:
                    pdf.set_font("Arial", size=font_size)
                    if "Hindi" in sel_font: # Warning agar file missing hai
                        st.warning("Hindi font file nahi mili! Arial use ho raha hai.")

                # PDF Write
                try:
                    pdf.multi_cell(0, 10, txt=edited_text)
                    pdf.output("edited_output.pdf")
                    with open("edited_output.pdf", "rb") as f:
                        st.success("✅ PDF Ban gayi!")
                        st.download_button("📥 Download PDF", f, file_name="edited_hindi_doc.pdf")
                except Exception as e:
                    st.error(f"Error: {e}")
            # ... (Upar ka code waisa hi rahega) ...

            if st.button("Save & Download PDF"):
                pdf = FPDF()
                pdf.add_page()
                
                # --- FINAL FONT LOGIC (Is logic ko dhyan se dekhein) ---
                
                # 1. Sabse pehle Hindi Font file ka pata lagayein
                font_path = "Hindi.ttf"  # Make sure file name yahi ho
                
                # 2. Agar user ne 'Hindi' select kiya hai YA text mein Hindi hai
                # Hum check karenge ki kya font file maujood hai?
                if os.path.exists(font_path):
                    try:
                        # Hindi Font Register karein
                        pdf.add_font('HindiFont', '', font_path)
                        pdf.set_font('HindiFont', size=font_size)
                    except Exception as e:
                        st.error(f"Font Load Error: {e}")
                        pdf.set_font("Arial", size=font_size)
                else:
                    # Agar Hindi.ttf file nahi mili toh warning dega
                    st.warning("⚠️ 'Hindi.ttf' file nahi mili! Default Arial use ho raha hai (Hindi support nahi karega).")
                    pdf.set_font("Arial", size=font_size)

                # 3. PDF Write karna (Crash se bachne ke liye Try-Except)
                try:
                    pdf.multi_cell(0, 10, txt=edited_text)
                    pdf.output("final_output.pdf")
                    
                    with open("final_output.pdf", "rb") as f:
                        st.success("✅ PDF Ban gayi!")
                        st.download_button("📥 Download PDF", f, file_name="edited_hindi_doc.pdf")
                
                except UnicodeEncodeError:
                    st.error("❌ Error: Aap Hindi text save kar rahe hain lekin font 'Arial/Helvetica' select hai. Kripya GitHub par 'Hindi.ttf' upload karein.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    

# ==========================================
# TOOL 2: CREATE NEW (Same as before)
# ==========================================
elif choice == "Create New":
    st.header("📝 Naya Document")
    user_inp = st.text_area("Type karein...", height=300)
    sel_f = st.selectbox("Font", available_fonts)
    if st.button("Generate"):
        pdf = FPDF()
        pdf.add_page()
        if "Hindi" in sel_f and os.path.exists(fonts["Hindi"]):
            pdf.add_font("H", "", fonts["Hindi"])
            pdf.set_font("H", size=14)
        elif "Typewriter" in sel_f and os.path.exists(fonts["Typewriter"]):
            pdf.add_font("T", "", fonts["Typewriter"])
            pdf.set_font("T", size=14)
        else: pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, user_inp)
        pdf.output("new.pdf")
        with open("new.pdf", "rb") as f: st.download_button("Download", f)

# ==========================================
# TOOL 3: CONVERT (Same as before)
# ==========================================
elif choice == "Convert":
    st.header("Convert PDF to Word")
    u_file = st.file_uploader("PDF Upload", type='pdf')
    if u_file and st.button("Convert"):
        with open("temp.pdf", "wb") as f: f.write(u_file.read())
        cv = Converter("temp.pdf")
        cv.convert("conv.docx")
        cv.close()
        with open("conv.docx", "rb") as f: st.download_button("Download Word", f)
            

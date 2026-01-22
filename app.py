import streamlit as st
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pytesseract
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Hindi PDF Editor", layout="wide")
st.title("📄 Hindi PDF Editor (Final Fix)")

# --- DEBUGGING: Check Files ---
# Ye user ko dikhayega ki GitHub par asal mein kaunsi files hain
st.sidebar.subheader("📂 Files on Server:")
files_on_server = os.listdir('.')
st.sidebar.write(files_on_server)

# --- FONT FILE NAMES (Yahan wo naam likhein jo Sidebar mein dikh raha hai) ---
# Agar sidebar mein 'hind.ttf' dikh raha hai, to yahan bhi 'hind.ttf' likhein
hindi_font_name = "Hindi.ttf"       
typewriter_font_name = "Typewriter.ttf"

# --- MAIN LOGIC ---
st.header("✏️ Hindi PDF Edit & Save")

uploaded_file = st.file_uploader("PDF Upload Karein", type=['pdf'], key="ocr_upload")

# --- TEXT EXTRACTION ---
extracted_text = ""
if uploaded_file:
    use_ocr = st.toggle("Use OCR Mode", value=True) # Default ON rakha hai
    if use_ocr:
        with st.spinner("Scanning..."):
            try:
                images = convert_from_bytes(uploaded_file.read())
                for img in images:
                    extracted_text += pytesseract.image_to_string(img, lang='hin+eng') + "\n"
            except Exception as e:
                st.error(f"OCR Error: {e}")
    else:
        st.info("Direct text mode (Not recommended for Hindi)")

# --- EDITOR ---
if extracted_text:
    col1, col2 = st.columns([2, 1])
    with col1:
        final_text = st.text_area("Editor", value=extracted_text, height=600)
    
    with col2:
        st.subheader("Save Settings")
        font_choice = st.radio("Font Style:", ["Hindi (Mangal)", "Typewriter", "English"])
        font_size = st.slider("Size:", 10, 30, 14)
        
        if st.button("Save PDF"):
            pdf = FPDF()
            pdf.add_page()
            
            # --- CRASH PROOF FONT LOGIC ---
            font_loaded = False
            
            # 1. Hindi Font Attempt
            if font_choice == "Hindi (Mangal)":
                if os.path.exists(hindi_font_name):
                    pdf.add_font("MyHindi", "", hindi_font_name)
                    pdf.set_font("MyHindi", size=font_size)
                    font_loaded = True
                else:
                    st.error(f"❌ Error: '{hindi_font_name}' file nahi mili! Sidebar check karein ki file ka naam kya hai.")
            
            # 2. Typewriter Font Attempt
            elif font_choice == "Typewriter":
                if os.path.exists(typewriter_font_name):
                    pdf.add_font("MyType", "", typewriter_font_name)
                    pdf.set_font("MyType", size=font_size)
                    font_loaded = True
                else:
                    st.error(f"❌ Error: '{typewriter_font_name}' file nahi mili!")

            # 3. Default (English)
            else:
                pdf.set_font("Arial", size=font_size)
                font_loaded = True # Arial hamesha hota hai

            # --- WRITING PDF (Try-Except Block) ---
            if font_loaded:
                try:
                    pdf.multi_cell(0, 10, final_text)
                    pdf.output("final.pdf")
                    with open("final.pdf", "rb") as f:
                        st.success("✅ PDF Ban gayi!")
                        st.download_button("Download Now", f, file_name="edited.pdf")
                
                except UnicodeEncodeError:
                    st.error("🚨 Encoding Error: Aap Hindi text save kar rahe hain lekin font English (Arial) select ho gaya hai.")
                    st.info("💡 Solution: Upar Font Style mein 'Hindi' select karein aur ensure karein ki 'Hindi.ttf' file upload hai.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("⚠️ Font file missing hone ki wajah se PDF save nahi hui.")

else:
    if uploaded_file:
        st.warning("Text extract nahi hua. Kya 'packages.txt' file bani hai?")
        

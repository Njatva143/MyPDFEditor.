import streamlit as st
from fpdf import FPDF
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Auto-Font PDF Editor", layout="wide")
st.title("📄 Auto-Font Hindi & Typewriter Editor")

# --- AUTO-DETECT FONTS ---
# Ye check karega ki aapne GitHub par font upload kiye hain ya nahi
fonts = {
    "Hindi": "Hindi.ttf",           # GitHub par file ka naam yahi hona chahiye
    "Typewriter": "Typewriter.ttf", # GitHub par file ka naam yahi hona chahiye
    "English": "Arial"              # Default system font
}

# Check availability
available_fonts = ["Arial (Standard)"]
if os.path.exists(fonts["Hindi"]):
    available_fonts.insert(0, "Hindi (Automatic)")
if os.path.exists(fonts["Typewriter"]):
    available_fonts.append("Typewriter (Automatic)")

# --- SIDEBAR ---
menu = ["Edit PDF", "Create PDF", "Convert PDF to Word"]
choice = st.sidebar.selectbox("Select Tool", menu)

# ============================
# TOOL 1: EDIT EXISTING PDF
# ============================
if choice == "Edit PDF":
    st.header("✏️ Edit PDF (Auto-Fonts)")
    uploaded_file = st.file_uploader("PDF File Upload", type=['pdf'])

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text_content = ""
        for page in reader.pages:
            text_content += (page.extract_text() or "") + "\n"

        col1, col2 = st.columns([2, 1])
        with col1:
            edited_text = st.text_area("Editor", value=text_content, height=400)
        
        with col2:
            st.subheader("Font Settings")
            # Yahan ab user ko baar-baar upload nahi karna padega
            selected_font_name = st.selectbox("Font Style Chunein:", available_fonts)
            font_size = st.slider("Size", 10, 30, 14)
            
            # Agar koi aur font chahiye to option
            custom_font = st.file_uploader("Koi aur font chahiye? (Optional)", type=['ttf'])

        if st.button("Save & Download"):
            pdf = FPDF()
            pdf.add_page()

            # --- SMART FONT LOGIC ---
            font_path_to_use = None
            font_family = "Arial"

            # 1. Agar user ne abhi file upload ki hai
            if custom_font:
                with open("temp_user.ttf", "wb") as f:
                    f.write(custom_font.read())
                font_path_to_use = "temp_user.ttf"
                font_family = "UserFont"
            
            # 2. Agar GitHub wala Hindi font select kiya
            elif "Hindi" in selected_font_name and os.path.exists(fonts["Hindi"]):
                font_path_to_use = fonts["Hindi"]
                font_family = "HindiAuto"
            
            # 3. Agar GitHub wala Typewriter font select kiya
            elif "Typewriter" in selected_font_name and os.path.exists(fonts["Typewriter"]):
                font_path_to_use = fonts["Typewriter"]
                font_family = "TypewriterAuto"
            
            # Font Register karna
            if font_path_to_use:
                try:
                    pdf.add_font(font_family, '', font_path_to_use)
                    pdf.set_font(font_family, size=font_size)
                except Exception as e:
                    st.error(f"Font Error: {e}")
                    pdf.set_font("Arial", size=font_size)
            else:
                pdf.set_font("Arial", size=font_size)

            # PDF Save
            try:
                pdf.multi_cell(0, 8, txt=edited_text)
                pdf.output("final_output.pdf")
                with open("final_output.pdf", "rb") as f:
                    st.success("✅ PDF Ready!")
                    st.download_button("📥 Download PDF", f, file_name="edited_doc.pdf")
            except Exception as e:
                st.error(f"Error: {e}. (Shayad Hindi text hai aur font select nahi kiya)")

# ============================
# TOOL 2: CREATE NEW PDF
# ============================
elif choice == "Create PDF":
    st.header("📝 New Document")
    user_input = st.text_area("Type here...", height=300)
    
    sel_font = st.selectbox("Font", available_fonts)
    
    if st.button("Generate"):
        pdf = FPDF()
        pdf.add_page()
        
        # Logic same as above (Simplified)
        if "Hindi" in sel_font:
            pdf.add_font("Hindi", "", fonts["Hindi"])
            pdf.set_font("Hindi", size=14)
        elif "Typewriter" in sel_font:
            pdf.add_font("Typewriter", "", fonts["Typewriter"])
            pdf.set_font("Typewriter", size=14)
        else:
            pdf.set_font("Arial", size=12)
            
        pdf.multi_cell(0, 10, user_input)
        pdf.output("new.pdf")
        with open("new.pdf", "rb") as f:
            st.download_button("Download", f, "new.pdf")

# ============================
# TOOL 3: CONVERT
# ============================
elif choice == "Convert PDF to Word":
    st.subheader("Convert to Word")
    f = st.file_uploader("Upload PDF", type='pdf')
    if f and st.button("Convert"):
        with open("temp.pdf", "wb") as file:
            file.write(f.read())
        cv = Converter("temp.pdf")
        cv.convert("conv.docx")
        cv.close()
        with open("conv.docx", "rb") as file:
            st.download_button("Download Word", file, "converted.docx")
            

import streamlit as st
from pdf2docx import Converter
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="PDF to Word Converter", layout="wide")
st.title("📄 PDF to Editable Word (Linux Safe)")

st.info("💡 **Kaise Edit Karein:** Ye tool apki PDF ko **MS Word** file bana dega. Aap us file ko download karein aur apne Mobile/Laptop mein Text edit karke wapas PDF save kar lein. Yehi sabse best tarika hai existing text badalne ka.")

# --- MAIN LOGIC ---
st.header("🛠️ Upload PDF to Convert")

uploaded_file = st.file_uploader("PDF File Upload Karein", type=['pdf'])

if uploaded_file:
    if st.button("Convert to Word (Docx)"):
        with st.spinner("Converting... (Layout save ho raha hai)"):
            try:
                # 1. Save Uploaded PDF Temporarily
                with open("temp_input.pdf", "wb") as f:
                    f.write(uploaded_file.read())
                
                # 2. Convert PDF to Word
                # Ye library Linux par bhi perfect chalti hai
                cv = Converter("temp_input.pdf")
                cv.convert("final_editable.docx", start=0, end=None)
                cv.close()
                
                # 3. Download Button
                with open("final_editable.docx", "rb") as f:
                    st.success("✅ File Convert Ho Gayi!")
                    st.download_button(
                        label="📥 Download Word File",
                        data=f,
                        file_name="Edited_Document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"Error: {e}")
            
            # 4. Cleanup (Optional)
            if os.path.exists("temp_input.pdf"):
                os.remove("temp_input.pdf")
                

import streamlit as st
from pdf2docx import Converter
from docx2pdf import convert
import os
import pythoncom  # Windows ke liye zaroori hai (Linux par skip ho jayega)

# --- APP CONFIG ---
st.set_page_config(page_title="Professional PDF Editor", layout="wide")
st.title("📄 PDF to Word (True Editor)")

st.info("💡 **Sach:** PDF ke andar direct text edit karna possible nahi hai. Isliye hum ise **Word** mein badal rahe hain taaki aap **maujood text** ko aaram se edit kar sakein.")

# --- SIDEBAR ---
choice = st.sidebar.radio("Kya karna hai?", ["PDF se Word (Edit karne ke liye)", "Word se PDF (Wapas save karne ke liye)"])

# ==========================================
# 1. PDF TO WORD (EDITABLE)
# ==========================================
if choice == "PDF se Word (Edit karne ke liye)":
    st.header("🛠️ PDF ko Editable Word banayein")
    
    uploaded_file = st.file_uploader("PDF File Upload Karein", type=['pdf'])
    
    if uploaded_file:
        if st.button("Convert to Word (Docx)"):
            with st.spinner("Converting... (Isme Layout same rahega)"):
                # 1. Save PDF temporarily
                with open("temp_input.pdf", "wb") as f:
                    f.write(uploaded_file.read())
                
                # 2. Convert to Docx
                cv = Converter("temp_input.pdf")
                # start=0, end=None means all pages
                cv.convert("editable_file.docx", start=0, end=None)
                cv.close()
                
                # 3. Download Button
                with open("editable_file.docx", "rb") as f:
                    st.success("✅ File Convert Ho Gayi!")
                    st.download_button(
                        label="📥 Download Editable Word File",
                        data=f,
                        file_name="Edited_File.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            
            st.markdown("""
            ### 📝 अब एडिट कैसे करें?
            1. ऊपर दी गई **Word File** डाउनलोड करें।
            2. इसे अपने मोबाइल (WPS Office) या कंप्यूटर (MS Word) में खोलें।
            3. अब आप **मौजूद टेक्स्ट** को मिटा सकते हैं और नया लिख सकते हैं।
            4. अगर आपको **'Typewriter'** फॉन्ट चाहिए, तो Word में फॉन्ट लिस्ट से 'Kruti Dev' सेलेक्ट करें।
            """)

# ==========================================
# 2. WORD TO PDF (FINAL SAVE)
# ==========================================
elif choice == "Word se PDF (Wapas save karne ke liye)":
    st.header("💾 Word ko Wapas PDF banayein")
    
    docx_file = st.file_uploader("Edited Word File Upload Karein", type=['docx'])
    
    if docx_file:
        if st.button("Convert back to PDF"):
            # Note: Server par Word to PDF conversion ke liye LibreOffice chahiye hota hai.
            # Python libraries perfect conversion nahi de paati bina MS Word install kiye.
            # Lekin hum 'docx2pdf' try karenge (Windows servers ke liye).
            
            st.warning("⚠️ Note: Best result ke liye apne Word App mein hi 'Save as PDF' karein.")
            
            # Saving logic for specialized servers
            with open("temp_edit.docx", "wb") as f:
                f.write(docx_file.read())
            
            try:
                # Koshish karenge convert karne ki
                convert("temp_edit.docx", "final_output.pdf")
                
                with open("final_output.pdf", "rb") as f:
                    st.success("✅ PDF Taiyar Hai!")
                    st.download_button("📥 Download Final PDF", f, file_name="Final_Print.pdf")
            except:
                st.error("Server par MS Word installed nahi hai. Kripya apne phone/PC mein Word App se hi 'Save as PDF' karein.")
                

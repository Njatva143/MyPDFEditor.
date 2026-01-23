import streamlit as st
from streamlit_drawable_canvas import st_canvas
from pdf2image import convert_from_bytes
from pdf2docx import Converter
from fpdf import FPDF
from PIL import Image
from docx import Document
import io
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ultimate Editor & Converter", layout="wide")
st.title("🛠️ All-in-One: Paint Editor & Converter")

# --- SIDEBAR MENU ---
st.sidebar.title("🚀 Menu")
app_mode = st.sidebar.radio("Select Tool:", ["Direct Paint Editor (Eraser/Write)", "Universal Converter"])

# ==================================================
# SECTION 1: DIRECT CANVAS EDITOR (PAINT STYLE)
# ==================================================
if app_mode == "Direct Paint Editor (Eraser/Write)":
    st.header("🎨 Direct Paint Editor")
    st.markdown("PDF/Image upload karein. **'Eraser Box'** se mitayein aur **'Text'** se likhein.")

    # Upload
    uploaded_file = st.file_uploader("Upload File (PDF/JPG)", type=["pdf", "jpg", "png"], key="canvas_upl")

    # Tools Setup
    col1, col2 = st.columns(2)
    with col1:
        drawing_mode = st.selectbox(
            "Tool Chunein:",
            ("transform", "rect", "text"),
            format_func=lambda x: {"transform": "🖐 Move/Hand", "rect": "⬜ Eraser (White Box)", "text": "🔤 Write Text"}.get(x, x)
        )
    with col2:
        stroke_width = st.slider("Size", 1, 50, 15)

    # Colors
    stroke_color = "#000000"
    if drawing_mode == "text":
        stroke_color = st.color_picker("Text Color", "#000000")
    elif drawing_mode == "rect":
        stroke_color = "#FFFFFF" # Eraser hamesha white

    if uploaded_file:
        image = None
        # PDF Handling
        if uploaded_file.name.lower().endswith(".pdf"):
            try:
                images = convert_from_bytes(uploaded_file.read())
                image = images[0] # First page
            except Exception as e: 
                st.error(f"PDF Error: {e}. Check packages.txt")
        else:
            image = Image.open(uploaded_file)

        if image:
            # FIX: Convert to RGB to prevent crash
            image = image.convert("RGB")
            
            # Resize Logic (Screen Fit)
            canvas_width = 800
            w_percent = (canvas_width / float(image.size[0]))
            canvas_height = int((float(image.size[1]) * float(w_percent)))
            bg_image = image.resize((canvas_width, canvas_height))

            # *** CANVAS COMPONENT ***
            # Note: Requirements.txt mein streamlit==1.32.0 hona zaroori hai
            try:
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 1)", # White fill for eraser
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_image=bg_image,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode=drawing_mode,
                    key="canvas_editor",
                )
            except Exception as e:
                st.error(f"Canvas Error: {e}")
                st.warning("⚠️ Solution: 'requirements.txt' mein 'streamlit==1.32.0' likhein.")

            # SAVE BUTTON
            if st.button("💾 Save as PDF"):
                if canvas_result is not None and canvas_result.image_data is not None:
                    # Combine layers
                    edited_frame = Image.fromarray(canvas_result.image_data.astype("uint8"), mode="RGBA")
                    final_output = bg_image.convert("RGBA")
                    final_output.alpha_composite(edited_frame)
                    final_output = final_output.convert("RGB")
                    
                    buf = io.BytesIO()
                    final_output.save(buf, format="PDF")
                    st.success("✅ Download Ready!")
                    st.download_button("📥 Download PDF", buf.getvalue(), "edited_doc.pdf")

# ==================================================
# SECTION 2: UNIVERSAL CONVERTER
# ==================================================
elif app_mode == "Universal Converter":
    st.header("🔄 Universal Format Converter")
    
    tab1, tab2, tab3 = st.tabs(["📄 PDF to Word", "📝 Word to PDF", "🖼️ Image to PDF"])

    # --- TAB 1: PDF TO WORD ---
    with tab1:
        st.subheader("Convert PDF -> Editable Word")
        p2w_file = st.file_uploader("PDF Upload", type=['pdf'], key="p2w")
        if p2w_file and st.button("Convert to Word"):
            with st.spinner("Converting..."):
                with open("temp.pdf", "wb") as f: f.write(p2w_file.read())
                cv = Converter("temp.pdf")
                cv.convert("converted.docx")
                cv.close()
                with open("converted.docx", "rb") as f:
                    st.download_button("📥 Download Word", f, "converted.docx")
                os.remove("temp.pdf")

    # --- TAB 2: WORD TO PDF ---
    with tab2:
        st.subheader("Convert Word -> PDF")
        w2p_file = st.file_uploader("Word Upload", type=['docx'], key="w2p")
        if w2p_file and st.button("Convert to PDF"):
            # Basic Conversion
            doc = Document(w2p_file)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for para in doc.paragraphs:
                text = para.text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, txt=text)
            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Download PDF", pdf_out, "word_to_pdf.pdf")

    # --- TAB 3: IMAGE TO PDF ---
    with tab3:
        st.subheader("Convert Images -> PDF")
        img_files = st.file_uploader("Select Images", type=['jpg', 'png'], accept_multiple_files=True, key="i2p")
        if img_files and st.button("Convert Images to PDF"):
            pil_images = [Image.open(f).convert("RGB") for f in img_files]
            if pil_images:
                buf = io.BytesIO()
                pil_images[0].save(buf, format="PDF", save_all=True, append_images=pil_images[1:])
                st.download_button("📥 Download PDF", buf.getvalue(), "images.pdf")
                

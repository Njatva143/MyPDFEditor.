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
st.title("🛠️ All-in-One: Editor & Universal Converter")

# --- HELPER: UNICODE TO KRUTI DEV CONVERTER ---
def convert_to_kruti(text):
    # Special replacements
    text = text.replace("त्र", "=k").replace("ज्ञ", "%").replace("श्र", "J")
    
    # Matra Shifting (Chhoti 'i')
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == 'ि':
            if i > 0:
                prev = chars[i-1]
                chars[i-1] = 'f'
                chars[i] = prev
        i += 1
    text = "".join(chars)
    
    # Mapping
    mapping = {
        'ा': 'k', 'ी': 'h', 'ु': 'q', 'ू': 'w', 'ृ': '`', 'े': 's', 'ै': 'S',
        'ो': 'ks', 'ौ': 'kS', 'ं': 'a', 'ँ': '¡', 'ः': '%', '्': 'd', '़': '+',
        'क': 'd', 'ख': '[', 'ग': 'x', 'घ': '?', 'च': 'p', 'छ': 'N', 'ज': 't', 'झ': '>',
        'ट': 'V', 'ठ': 'B', 'ड': 'M', 'ढ': '<', 'ण': '.', 'त': 'r', 'थ': 'F', 'द': 'n',
        'ध': 'è', 'न': 'u', 'प': 'i', 'फ': 'Q', 'ब': 'c', 'भ': 'H', 'म': 'e', 'य': ';',
        'र': 'j', 'ल': 'y', 'व': 'b', 'श': 'M', 'ष': 'k', 'स': 'l', 'ह': 'v',
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9',
        '.': 'A', ',': ',', '-': '-', '(': '¼', ')': '½'
    }
    
    new_text = ""
    for c in text: new_text += mapping.get(c, c)
    return new_text

# --- SIDEBAR MENU ---
st.sidebar.title("🚀 Menu")
app_mode = st.sidebar.radio("Select Tool:", ["Direct Paint Editor (Eraser/Write)", "Universal Converter"])

# ==================================================
# SECTION 1: DIRECT PAINT EDITOR
# ==================================================
if app_mode == "Direct Paint Editor (Eraser/Write)":
    st.header("🎨 Direct Paint Editor")
    
    uploaded_file = st.file_uploader("Upload File (PDF/JPG)", type=["pdf", "jpg", "png"], key="canvas_upl")
    
    col1, col2 = st.columns(2)
    with col1:
        drawing_mode = st.selectbox(
            "Tool Chunein:",
            ("transform", "rect", "text"),
            format_func=lambda x: {"transform": "🖐 Move/Hand", "rect": "⬜ Eraser (White Box)", "text": "🔤 Write Text"}.get(x, x)
        )
    with col2:
        stroke_width = st.slider("Size", 1, 50, 15)

    stroke_color = "#000000"
    if drawing_mode == "text": stroke_color = st.color_picker("Text Color", "#000000")
    elif drawing_mode == "rect": stroke_color = "#FFFFFF"

    if uploaded_file:
        image = None
        if uploaded_file.name.lower().endswith(".pdf"):
            try:
                images = convert_from_bytes(uploaded_file.read())
                image = images[0]
            except Exception as e: st.error(f"PDF Error: {e}")
        else:
            image = Image.open(uploaded_file)

        if image:
            image = image.convert("RGB")
            # Canvas logic
            canvas_width = 800
            w_percent = (canvas_width / float(image.size[0]))
            canvas_height = int((float(image.size[1]) * float(w_percent)))
            bg_image = image.resize((canvas_width, canvas_height))

            try:
                canvas_result = st_canvas(
                    fill_color="rgba(255, 255, 255, 1)", 
                    stroke_width=stroke_width,
                    stroke_color=stroke_color,
                    background_image=bg_image,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode=drawing_mode,
                    key="canvas_editor",
                )
                
                if st.button("💾 Save as PDF"):
                    if canvas_result.image_data is not None:
                        edited_frame = Image.fromarray(canvas_result.image_data.astype("uint8"), mode="RGBA")
                        final_output = bg_image.convert("RGBA")
                        final_output.alpha_composite(edited_frame)
                        final_output = final_output.convert("RGB")
                        buf = io.BytesIO()
                        final_output.save(buf, format="PDF")
                        st.download_button("📥 Download PDF", buf.getvalue(), "edited.pdf")
            except: st.warning("Streamlit version error. Check requirements.txt")

# ==================================================
# SECTION 2: UNIVERSAL CONVERTER
# ==================================================
elif app_mode == "Universal Converter":
    st.header("🔄 Universal Format Converter")
    
    # --- ADDED TAB 4: TYPEWRITER CONVERTER ---
    tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF to Word", "📝 Word to PDF", "🖼️ Image to PDF", "🔠 Text to Typewriter PDF"])

    # TAB 1: PDF to Word
    with tab1:
        st.subheader("PDF -> Word")
        f = st.file_uploader("PDF Upload", type=['pdf'], key="p2w")
        if f and st.button("Convert to Word"):
            with open("t.pdf", "wb") as file: file.write(f.read())
            cv = Converter("t.pdf")
            cv.convert("c.docx")
            cv.close()
            with open("c.docx", "rb") as file: st.download_button("Download Word", file, "c.docx")

    # TAB 2: Word to PDF
    with tab2:
        st.subheader("Word -> PDF")
        f = st.file_uploader("Word Upload", type=['docx'], key="w2p")
        if f and st.button("Convert to PDF"):
            try:
                doc = Document(f)
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for p in doc.paragraphs:
                    safe_text = p.text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, safe_text)
                st.download_button("Download PDF", pdf.output(dest='S').encode('latin-1'), "doc.pdf")
            except Exception as e: st.error(f"Error: {e}")

    # TAB 3: Image to PDF
    with tab3:
        st.subheader("Images -> PDF")
        imgs = st.file_uploader("Select Images", type=['jpg', 'png'], accept_multiple_files=True)
        if imgs and st.button("Make PDF"):
            pil_imgs = [Image.open(i).convert("RGB") for i in imgs]
            b = io.BytesIO()
            pil_imgs[0].save(b, format="PDF", save_all=True, append_images=pil_imgs[1:])
            st.download_button("Download PDF", b.getvalue(), "imgs.pdf")

    # --- TAB 4: NEW TYPEWRITER CONVERTER ---
    with tab4:
        st.subheader("🔠 Convert Normal Text to Typewriter PDF")
        st.info("Mobile Hindi (Unicode) yahan paste karein, hum use Typewriter Font (Kruti Dev) mein convert karke PDF denge.")
        
        user_text = st.text_area("Yahan Hindi Text Likhein:", height=200)
        font_sz = st.slider("Font Size", 10, 40, 16)
        
        if st.button("Convert & Download PDF"):
            if os.path.exists("Typewriter.ttf"):
                pdf = FPDF()
                pdf.add_page()
                
                # Load Typewriter Font
                pdf.add_font("Kruti", "", "Typewriter.ttf")
                pdf.set_font("Kruti", size=font_sz)
                
                # Convert Text Logic
                converted_text = convert_to_kruti(user_text)
                
                # Write to PDF
                try:
                    pdf.multi_cell(0, 10, txt=converted_text)
                    
                    pdf_out = pdf.output(dest='S').encode('latin-1')
                    st.success("✅ Converted Successfully!")
                    st.download_button("📥 Download Typewriter PDF", pdf_out, "typewriter_output.pdf")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("❌ 'Typewriter.ttf' file missing hai! GitHub par upload karein.")
                

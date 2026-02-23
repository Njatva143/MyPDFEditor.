import streamlit as st
import os

# ==========================================
# 🛑 CRITICAL FIX (DO NOT REMOVE)
# Streamlit 1.34+ Breakage Fix
# ==========================================
try:
    # Canvas library purane Streamlit function ko dhund rahi hai jo ab gayab hai.
    # Hum use wapas inject kar rahe hain.
    import streamlit.elements.image
    from streamlit.elements.utils import image_to_url
    
    if not hasattr(streamlit.elements.image, 'image_to_url'):
        streamlit.elements.image.image_to_url = image_to_url
except Exception as e:
    pass # Agar ye fail hua, to hum kuch nahi kar sakte
# ==========================================

# --- PAGE CONFIG ---
st.set_page_config("PDF Live Editor", layout="wide")
st.title("📄 PDF Live Editor & Converter")

# ==========================================
# 🛡️ SAFE IMPORTS
# ==========================================
try:
    from streamlit_drawable_canvas import st_canvas
    from pdf2image import convert_from_bytes
    from PIL import Image, ImageDraw
    from PyPDF2 import PdfReader, PdfWriter
    from docx import Document
    from pdf2docx import Converter
    from fpdf import FPDF
    import io
    import tempfile
except ImportError as e:
    st.error(f"🚨 Library Missing: {e}")
    st.info("Please update 'requirements.txt' and 'packages.txt' on GitHub.")
    st.stop()

# ==========================================
# 🛠️ CONFIG & UTILITIES
# ==========================================
MAX_PAGES = 10
DPI = 150
CANVAS_WIDTH = 800

def word_to_pdf_buffer(word_file):
    doc = Document(word_file)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for p in doc.paragraphs:
        safe_text = p.text.encode('latin-1', 'replace').decode('latin-1')
        if safe_text.strip():
            pdf.multi_cell(0, 10, safe_text)
            pdf.ln(1)
    return bytes(pdf.output())

def pdf_to_images(file_bytes):
    try:
        return convert_from_bytes(file_bytes, dpi=DPI)
    except Exception as e:
        st.error("❌ PDF Error: 'poppler-utils' missing in packages.txt")
        st.stop()

def resize_img(img):
    ratio = CANVAS_WIDTH / img.width
    return img.resize((CANVAS_WIDTH, int(img.height * ratio)))

def save_pdf(pages_list):
    if not pages_list: return None
    buf = io.BytesIO()
    rgb = [i.convert("RGB") for i in pages_list]
    rgb[0].save(buf, format="PDF", save_all=True, append_images=rgb[1:])
    return buf.getvalue()

# ==========================================
# 🧠 SESSION STATE
# ==========================================
if "file_ref" not in st.session_state:
    st.session_state.file_ref = None
if "editor_pages" not in st.session_state:
    st.session_state.editor_pages = []
if "canvas_key" not in st.session_state:
    st.session_state.canvas_key = 0

# ==========================================
# 🚀 MAIN APP LOGIC
# ==========================================
st.sidebar.markdown("### 🛠️ Menu")
mode = st.sidebar.radio("Select Mode", ["📝 Live Editor", "Word ↔ PDF"])

# --- 1. LIVE EDITOR MODE ---
if mode == "📝 Live Editor":
    st.info("ℹ️ **Live Edit:** Select **'Whitener'** to erase text, then **'Text'** to type new.")
    
    uploaded = st.file_uploader("Upload PDF or Word", type=["pdf", "docx"])

    if uploaded:
        # Load Logic
        if st.session_state.file_ref != uploaded.name:
            st.session_state.file_ref = uploaded.name
            st.session_state.canvas_key = 0 # Reset Key
            
            with st.spinner("Loading..."):
                if uploaded.name.endswith(".pdf"):
                    data = uploaded.read()
                else:
                    data = word_to_pdf_buffer(uploaded)
                st.session_state.editor_pages = pdf_to_images(data)
        
        # Display Editor
        current_pages = st.session_state.editor_pages
        if current_pages:
            col_nav1, col_nav2 = st.columns([1, 4])
            with col_nav1:
                pg_num = st.number_input("Page No", 1, len(current_pages), 1) - 1
            
            # Toolbar
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                tool = st.selectbox("Tool", ["Hand", "⬜ Whitener", "🔤 Text", "🖊️ Pen"])
            with c2:
                sz = st.slider("Size", 5, 40, 15)
            with c3:
                clr = st.color_picker("Color", "#000000")
            
            # Tool Settings
            d_mode = "transform"
            fill = "rgba(0,0,0,0)"
            if tool == "⬜ Whitener":
                d_mode = "rect"
                clr = "#FFFFFF"
                fill = "#FFFFFF"
            elif tool == "🔤 Text": d_mode = "text"
            elif tool == "🖊️ Pen": d_mode = "freedraw"

            # Prepare Image
            img = current_pages[pg_num].convert("RGB")
            bg_img = resize_img(img)
            
            # Unique Key for Realtime Update
            key = f"canvas_{uploaded.name}_{pg_num}_{st.session_state.canvas_key}"

            # --- LIVE CANVAS ---
            try:
                canvas = st_canvas(
                    fill_color=fill,
                    stroke_width=sz,
                    stroke_color=clr,
                    background_image=bg_img,
                    height=bg_img.height,
                    width=bg_img.width,
                    drawing_mode=d_mode,
                    key=key,
                    update_streamlit=True, # 🔥 LIVE FEATURE
                )
            except Exception as e:
                st.error(f"Canvas Error: {e}")
                st.stop()

            # --- SAVE & MERGE BUTTON ---
            col_save, col_down = st.columns(2)
            with col_save:
                if st.button("✅ Commit Changes (Apply)"):
                    if canvas.image_data is not None:
                        # Layer Merge Logic
                        fg = Image.fromarray(canvas.image_data.astype("uint8")).convert("RGBA")
                        bg = img.copy().convert("RGBA")
                        fg = fg.resize(bg.size)
                        combined = Image.alpha_composite(bg, fg).convert("RGB")
                        
                        # Save to State
                        st.session_state.editor_pages[pg_num] = combined
                        
                        # Reset Canvas Key
                        st.session_state.canvas_key += 1
                        st.success("Saved!")
                        st.rerun()

            with col_down:
                if st.button("📥 Download Final PDF"):
                    final_bytes = save_pdf(st.session_state.editor_pages)
                    st.download_button("Download PDF", final_bytes, "edited_live.pdf")

# --- 2. WORD CONVERTER ---
elif mode == "Word ↔ PDF":
    st.header("🔄 Word Converter")
    tab1, tab2 = st.tabs(["PDF -> Word", "Word -> PDF"])
    
    with tab1:
        f = st.file_uploader("PDF", type="pdf")
        if f and st.button("To Word"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(f.read())
                p_path = tmp.name
            d_path = p_path.replace(".pdf", ".docx")
            try:
                cv = Converter(p_path)
                cv.convert(d_path)
                cv.close()
                with open(d_path, "rb") as x:
                    st.download_button("Download Word", x.read(), "converted.docx")
            except Exception as e: st.error(e)

    with tab2:
        f = st.file_uploader("Word", type="docx")
        if f and st.button("To PDF"):
            try:
                data = word_to_pdf_buffer(f)
                st.download_button("Download PDF", data, "converted.pdf")
            except Exception as e: st.error(e)
                

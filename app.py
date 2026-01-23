import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates
from pdf2image import convert_from_bytes
import io
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Click Editor (PDF + Image)", layout="wide")
st.title("🖱️ Click & Edit (PDF & Images)")

# --- FONTS SETUP ---
fonts = {
    "Typewriter (Kruti Dev)": "Typewriter.ttf", 
    "Hindi (Mangal/Hind)": "Hindi.ttf",
    "English (Arial)": "arial.ttf"
}

# --- HELPER: KRUTI DEV CONVERTER ---
def convert_to_kruti(text):
    text = text.replace("त्र", "=k").replace("ज्ञ", "%").replace("श्र", "J")
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
    mapping = {
        'ा': 'k', 'ी': 'h', 'ु': 'q', 'ू': 'w', 'ृ': '`', 'े': 's', 'ै': 'S',
        'ो': 'ks', 'ौ': 'kS', 'ं': 'a', 'ँ': '¡', 'ः': '%', '्': 'd', '़': '+',
        'क': 'd', 'ख': '[', 'ग': 'x', 'घ': '?', 'च': 'p', 'छ': 'N', 'ज': 't', 'झ': '>',
        'ट': 'V', 'ठ': 'B', 'ड': 'M', 'ढ': '<', 'ण': '.', 'त': 'r', 'थ': 'F', 'द': 'n',
        'ध': 'è', 'न': 'u', 'प': 'i', 'फ': 'Q', 'ब': 'c', 'भ': 'H', 'म': 'e', 'य': ';',
        'र': 'j', 'ल': 'y', 'व': 'b', 'श': 'M', 'ष': 'k', 'स': 'l', 'ह': 'v',
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    new_text = ""
    for c in text: new_text += mapping.get(c, c)
    return new_text

# --- SESSION STATE ---
if "edits" not in st.session_state:
    st.session_state["edits"] = []

# --- SIDEBAR SETTINGS ---
st.sidebar.header("✏️ Edit Settings")

# 1. Text Controls
new_text = st.sidebar.text_input("Naya Text:", "New Value")
font_choice = st.sidebar.selectbox("Font Style", list(fonts.keys()))
f_size = st.sidebar.slider("Font Size", 10, 100, 24)
text_color = st.sidebar.color_picker("Text Color", "#000000")

# 2. Patch Controls (Whitener)
st.sidebar.markdown("---")
st.sidebar.write("🧹 **Patch (Whitener):**")
use_patch = st.sidebar.checkbox("Patch On/Off", value=True)
patch_color = st.sidebar.color_picker("Background Color", "#FFFFFF")

# 3. Undo Button
if st.sidebar.button("Undo Last Click"):
    if st.session_state["edits"]:
        st.session_state["edits"].pop()
        st.rerun()

if st.sidebar.button("Clear All"):
    st.session_state["edits"] = []
    st.rerun()

# --- MAIN UPLOAD SECTION ---
# Yahan maine PDF ka option jod diya hai
uploaded_file = st.file_uploader("Upload File (PDF, JPG, PNG)", type=['pdf', 'jpg', 'png', 'jpeg'])

if uploaded_file:
    # --- FILE PROCESSING ---
    image = None
    
    # Check karein file PDF hai ya Image
    if uploaded_file.name.lower().endswith('.pdf'):
        # PDF to Image Conversion
        try:
            images = convert_from_bytes(uploaded_file.read())
            
            # Agar PDF mein zyada pages hain to select karne ka option denge
            if len(images) > 1:
                page_sel = st.number_input("Page Number Select Karein", 1, len(images), 1)
                image = images[page_sel-1] # 0-index adjust
            else:
                image = images[0] # Pehla page
        except Exception as e:
            st.error(f"PDF Error: {e}. (Kya packages.txt mein poppler-utils hai?)")
    else:
        # Image Handling
        image = Image.open(uploaded_file).convert("RGB")

    # --- IF IMAGE IS READY ---
    if image:
        # Draw previous edits
        draw = ImageDraw.Draw(image)
        
        for edit in st.session_state["edits"]:
            x, y, txt, fname, fsz, tcl, pcl, pch = edit
            
            # Font Load
            fpath = fonts[fname]
            try:
                if os.path.exists(fpath):
                    fnt = ImageFont.truetype(fpath, fsz)
                else:
                    fnt = ImageFont.load_default()
            except: fnt = ImageFont.load_default()
            
            # Convert text if typewriter
            final_txt = txt
            if "Typewriter" in fname:
                final_txt = convert_to_kruti(txt)
            
            # Draw Patch
            if pch:
                bbox = draw.textbbox((x, y), final_txt, font=fnt)
                # Thoda padding
                pbox = (bbox[0]-5, bbox[1]-2, bbox[2]+5, bbox[3]+2)
                draw.rectangle(pbox, fill=pcl)
            
            # Draw Text
            draw.text((x, y), final
            

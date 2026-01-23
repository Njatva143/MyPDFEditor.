import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from streamlit_image_coordinates import streamlit_image_coordinates
import io
import os

st.set_page_config(page_title="Photo Text Editor", layout="wide")
st.title("🖼️ Image Text Replacer (Photo Editor)")

# --- FONT SETUP ---
# Fonts wahi purane folders se uthayega
fonts = {
    "Typewriter (Kruti Dev)": "Typewriter.ttf", 
    "Hindi (Mangal/Hind)": "Hindi.ttf",
    "English (Bold)": "arial.ttf" # System font fallback
}

# --- HELPER: KRUTI DEV CONVERTER ---
def convert_to_kruti(text):
    # Simple converter logic for display
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
if "img_edits" not in st.session_state:
    st.session_state["img_edits"] = []

# --- SIDEBAR CONTROLS ---
st.sidebar.header("✏️ Editor Settings")

# 1. Text Settings
new_text = st.sidebar.text_input("Naya Text Likhein:", "Yahan Likhein")
font_choice = st.sidebar.selectbox("Font Style", list(fonts.keys()))
f_size = st.sidebar.slider("Font Size", 10, 100, 30)
text_color = st.sidebar.color_picker("Text Color", "#000000")

# 2. Patch Settings (Whitener)
st.sidebar.markdown("---")
st.sidebar.write("🧹 **Purana Text Chupana (Patch):**")
use_patch = st.sidebar.checkbox("Patch Lagayein?", value=True)
patch_color = st.sidebar.color_picker("Background/Paper Color Match Karein", "#FFFFFF")
# Agar paper purana/yellow hai to upar se color pick karein

# 3. Clear Button
if st.sidebar.button("Undo Last Change"):
    if st.session_state["img_edits"]:
        st.session_state["img_edits"].pop()
        st.rerun()

# --- MAIN APP ---
uploaded_img = st.file_uploader("Image Upload (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_img:
    # Image Open
    image = Image.open(uploaded_img).convert("RGB")
    
    # --- DRAW SAVED EDITS ---
    draw = ImageDraw.Draw(image)
    
    for edit in st.session_state["img_edits"]:
        x, y, txt, fname, fsize, tcol, pcol, do_patch = edit
        
        # Font Load
        fpath = fonts[fname]
        try:
            if os.path.exists(fpath):
                fnt = ImageFont.truetype(fpath, fsize)
            else:
                fnt = ImageFont.load_default()
        except: fnt = ImageFont.load_default()
        
        # Typewriter Conversion
        final_txt = txt
        if "Typewriter" in fname:
            final_txt = convert_to_kruti(txt)
            
        # Draw Patch (Background Chupana)
        if do_patch:
            bbox = draw.textbbox((x, y), final_txt, font=fnt)
            # Thoda padding dete hain taaki purana text pura dhak jaye
            padded_box = (bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2)
            draw.rectangle(padded_box, fill=pcol)
            
        # Draw Text
        draw.text((x, y), final_txt, font=fnt, fill=tcol)

        # --- SHOW IMAGE & CLICK ---
    st.markdown("---")
    st.write("👇 **Image par wahan CLICK karein jahan text badalna hai:**")
    
    # 1. PEHLE CHECK KAREIN KI IMAGE HAI YA NAHI
    if image:
        try:
            # Ye component click capture karega
            value = streamlit_image_coordinates(image, key="img_click")
            
            if value is not None:
                # Check Duplicate Click
                last_pt = st.session_state["img_edits"][-1] if st.session_state["img_edits"] else None
                is_dup = False
                if last_pt:
                    if abs(last_pt[0] - value['x']) < 10 and abs(last_pt[1] - value['y']) < 10:
                        is_dup = True
                        
                if not is_dup:
                    # Store Edit
                    st.session_state["img_edits"].append(
                        (value['x'], value['y'], new_text, font_choice, f_size, text_color, patch_color, use_patch)
                    )
                    st.rerun()
        except Exception as e:
            # Agar upar wala component fail ho jaye, to ye Error dikhayega
            st.error(f"Clickable Image load nahi hui. Error: {e}")
            st.warning("Niche Normal Image dikh rahi hai (Lekin click kaam nahi karega):")
            st.image(image, caption="Uploaded Image (View Only)")
    else:
        st.error("Image object khali hai. Shayad upload fail ho gaya.")

    # --- DOWNLOAD ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        # Save as JPG
        buf_jpg = io.BytesIO()
        image.save(buf_jpg, format="JPEG")
        st.download_button("📥 Download as Image (JPG)", buf_jpg.getvalue(), "edited_image.jpg")
    
    with col2:
        # Save as PDF
        buf_pdf = io.BytesIO()
        image.save(buf_pdf, format="PDF")
        st.download_button("📥 Download as PDF", buf_pdf.getvalue(), "edited_image.pdf")
        

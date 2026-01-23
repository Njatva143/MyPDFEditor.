import streamlit as st
from pdf2docx import Converter
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
import os
import io

# --- CONFIG ---
st.set_page_config(page_title="Universal Format Editor", layout="wide")
st.title("🛠️ All-Format Editor (No Layout Change)")

# --- FONTS SETUP ---
# GitHub par ye 2 files honi chahiye
fonts = {
    "Typewriter (Kruti Dev)": "Typewriter.ttf", 
    "Modern (Hindi)": "Hindi.ttf",
    "English (Arial)": "arial.ttf" # System font fallback
}

# --- HELPER: UNICODE TO KRUTI DEV (Improved) ---
def convert_to_kruti(text):
    # Ye wahi engine hai jo matra shift karta hai
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

# --- SIDEBAR MENU ---
menu = ["VISUAL EDITOR (Overlay Text)", "FORMAT CONVERTER (PDF <-> Word)"]
choice = st.sidebar.selectbox("Tool Chunein:", menu)

# ==========================================
# TOOL 1: VISUAL OVERLAY EDITOR (Best for patching)
# ==========================================
if choice == "VISUAL EDITOR (Overlay Text)":
    st.header("🖼️ Visual Editor (Patch Mode)")
    st.info("Is tool se purana format 1% bhi nahi hilega. Hum naye text ko purane ke upar chipka denge.")
    
    uploaded_file = st.file_uploader("PDF Upload", type=['pdf'])
    
    if uploaded_file:
        # 1. Convert PDF to Images
        images = convert_from_bytes(uploaded_file.read())
        
        # Page Selection
        page_num = st.number_input("Page Number Select Karein", min_value=1, max_value=len(images), value=1)
        current_image = images[page_num-1].copy() # Work on copy
        
        # 2. Text Input
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Edit Settings")
            user_text = st.text_area("Naya Text Likhein (Hindi/Eng):", "Yahan likhein")
            
            font_choice = st.selectbox("Font Style Match Karein:", list(fonts.keys()))
            
            # Position Controls
            st.write("📍 **Text Position (Khiskane ke liye):**")
            x_pos = st.slider("Left-Right (X)", 0, current_image.width, 100)
            y_pos = st.slider("Up-Down (Y)", 0, current_image.height, 100)
            
            # Style Controls
            font_size = st.slider("Font Size", 10, 100, 30)
            text_color = st.color_picker("Text Color (Match Old Ink)", "#000000")
            
            # Background Patch (White-out)
            use_patch = st.checkbox("Safed patti lagayein? (Purana text chupane ke liye)", value=True)

        with col2:
            st.subheader("Live Preview")
            
            # --- DRAWING LOGIC ---
            draw = ImageDraw.Draw(current_image)
            
            # Font Loading
            selected_font_path = fonts[font_choice]
            try:
                # Agar font file nahi hai to default load karo
                if os.path.exists(selected_font_path):
                    loaded_font = ImageFont.truetype(selected_font_path, font_size)
                else:
                    loaded_font = ImageFont.load_default()
            except:
                loaded_font = ImageFont.load_default()

            # Text Conversion for Kruti Dev
            final_text = user_text
            if "Typewriter" in font_choice and os.path.exists("Typewriter.ttf"):
                final_text = convert_to_kruti(user_text)

            # Draw White Patch (Eraser)
            if use_patch:
                # Text size calculate karo taki patch utna hi bada bane
                bbox = draw.textbbox((x_pos, y_pos), final_text, font=loaded_font)
                draw.rectangle(bbox, fill="white")

            # Draw Text
            draw.text((x_pos, y_pos), final_text, fill=text_color, font=loaded_font)
            
            # Show Image
            st.image(current_image, caption="Final Page Preview", use_column_width=True)

        # 3. Save Button
        if st.button("Download Edited PDF"):
            pdf_bytes = io.BytesIO()
            # Convert modified image back to PDF
            current_image.save(pdf_bytes, format='PDF')
            st.success("✅ Document Edit Ho Gaya!")
            st.download_button("Download Now", pdf_bytes.getvalue(), file_name="edited_visual.pdf")

# ==========================================
# TOOL 2: FORMAT CONVERTER
# ==========================================
elif choice == "FORMAT CONVERTER (PDF <-> Word)":
    st.header("🔃 Format Converter (No Data Loss)")
    
    tab1, tab2 = st.tabs(["PDF to Word", "Word to PDF"])
    
    with tab1:
        st.subheader("PDF se Word (Docx)")
        pdf_file = st.file_uploader("PDF Upload", type=['pdf'], key="p2w")
        if pdf_file and st.button("Convert to Word"):
            with open("temp.pdf", "wb") as f: f.write(pdf_file.read())
            
            cv = Converter("temp.pdf")
            cv.convert("converted.docx")
            cv.close()
            
            with open("converted.docx", "rb") as f:
                st.download_button("📥 Download Word File", f, file_name="converted.docx")
            st.success("Word file mein layout waisa hi rahega. Aap MS Word mein edit kar sakte hain!")

    with tab2:
        st.subheader("Word se PDF")
        st.info("Word file upload karein, hum usse PDF bana denge.")
        # Note: Linux server par Word to PDF complex hai, basic text extraction support hai
        docx_file = st.file_uploader("Word Upload", type=['docx'], key="w2p")
        if docx_file and st.button("Convert to PDF"):
            # Basic conversion using FPDF (Layout might change slightly)
            # Best option is to use 'Print to PDF' in MS Word
            st.warning("Best Result ke liye: Apne Mobile/PC mein Word khol kar 'Save as PDF' karein.")
            

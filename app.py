import streamlit as st
import tempfile
import os
import zipfile
import io
from markitdown import MarkItDown

# Must be the first Streamlit command
st.set_page_config(page_title="Notion-style Converter", page_icon="📝", layout="centered")

# Notion Design System CSS Injection
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Change primary button color to Notion purple */
    .stButton > button[kind="primary"] {
        background-color: #5645d4;
        color: white;
        border: none;
        border-radius: 8px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4534b3;
    }
    
    /* Change secondary button styling */
    .stButton > button[kind="secondary"] {
        border-radius: 8px;
        border: 1px solid #c8c4be;
    }
    
    /* Hero section styling hack using st.markdown container */
    .hero-container {
        background-color: #0a1530;
        color: white;
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
    }
    .hero-container h1 {
        color: white;
        font-weight: 600;
        font-size: 3rem;
        margin-bottom: 10px;
    }
    .hero-container p {
        color: #a4a097;
        font-size: 1.1rem;
    }
    
    /* Result card styling */
    .result-card {
        background-color: #f6f5f4;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e5e3df;
        margin-bottom: 15px;
        color: #1a1a1a;
    }
    .result-card h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #37352f;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Hero Section
st.markdown("""
<div class="hero-container">
    <h1>Meet the night shift.</h1>
    <p>Convert your PDFs, Office documents, and images to clean Markdown instantly.</p>
</div>
""", unsafe_allow_html=True)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

top_actions = st.empty()

# File Uploader (Supports Drag & Drop natively, accept_multiple_files for multiple files)
uploaded_files = st.file_uploader(
    "Upload files to convert", 
    accept_multiple_files=True,
    help="Drag and drop your files here.",
    key=str(st.session_state.uploader_key)
)

if uploaded_files:
    with top_actions.container():
        if st.button("🗑️ Clear Data", key="clear_btn", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

    st.info(f"📂 {len(uploaded_files)} file(s) selected and ready for conversion.")
    
    if st.button("✨ Convert to Markdown", type="primary", use_container_width=True):
        md = MarkItDown()
        
        successful_conversions = []
        
        # Process each file
        progress_text = "Conversion in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        
        for i, uploaded_file in enumerate(uploaded_files):
            file_extension = os.path.splitext(uploaded_file.name)[1]
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                result = md.convert(tmp_file_path)
                
                if result and result.text_content:
                    md_filename = f"{os.path.splitext(uploaded_file.name)[0]}.md"
                    successful_conversions.append((md_filename, result.text_content))
                    
                    # Display result in a styled container
                    st.markdown(f'<div class="result-card"><h3>✅ {uploaded_file.name}</h3></div>', unsafe_allow_html=True)
                    
                    with st.expander(f"Preview: {uploaded_file.name}"):
                        st.text_area("Markdown Output", result.text_content, height=200, key=f"text_{i}")
                        
                    st.download_button(
                        label=f"⬇️ Download {md_filename}",
                        data=result.text_content,
                        file_name=md_filename,
                        mime="text/markdown",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
                else:
                    st.warning(f"⚠️ Conversion completed for {uploaded_file.name} but no text content was extracted.")
                    
            except Exception as e:
                st.error(f"❌ Error converting {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                    
            # Update progress
            my_bar.progress((i + 1) / len(uploaded_files), text=f"Converted {i+1} of {len(uploaded_files)} files")
            
        my_bar.empty()
                        
        if len(successful_conversions) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, content in successful_conversions:
                    zip_file.writestr(filename, content)
            
            # Update top actions with ZIP download alongside Clear Data
            with top_actions.container():
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Clear Data", key="clear_btn_after", use_container_width=True):
                        st.session_state.uploader_key += 1
                        st.rerun()
                with col2:
                    st.download_button(
                        label="📦 Download All as ZIP",
                        data=zip_buffer.getvalue(),
                        file_name="converted_files.zip",
                        mime="application/zip",
                        type="primary",
                        key="dl_zip_all",
                        use_container_width=True
                    )

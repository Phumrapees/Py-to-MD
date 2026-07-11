import streamlit as st
import tempfile
import os
from markitdown import MarkItDown

st.set_page_config(page_title="MarkItDown Converter", page_icon="📝", layout="centered")

st.title("📝 File to Markdown Converter")
st.markdown("Convert various files (PDF, Word, Excel, PowerPoint, HTML, Images, Audio, etc.) to Markdown using [Microsoft's MarkItDown](https://github.com/microsoft/markitdown).")

uploaded_file = st.file_uploader("Upload a file to convert", type=None)

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    file_extension = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    st.info(f"File uploaded: {uploaded_file.name}")
    
    if st.button("Convert to Markdown", type="primary"):
        with st.spinner("Converting... Please wait."):
            try:
                # Initialize MarkItDown converter
                md = MarkItDown()
                
                # Perform conversion
                result = md.convert(tmp_file_path)
                
                if result and result.text_content:
                    st.success("Conversion successful!")
                    
                    st.subheader("Preview")
                    st.markdown(result.text_content)
                    
                    st.subheader("Raw Markdown")
                    st.text_area("Markdown Output", result.text_content, height=300)
                    
                    st.download_button(
                        label="Download Markdown File",
                        data=result.text_content,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                        mime="text/markdown"
                    )
                else:
                    st.warning("Conversion completed but no text content was extracted.")
                    
            except Exception as e:
                st.error(f"Error during conversion: {e}")
            finally:
                # Clean up the temporary file
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

st.markdown("---")
st.caption("Powered by [Streamlit](https://streamlit.io/) & [Microsoft MarkItDown](https://github.com/microsoft/markitdown)")

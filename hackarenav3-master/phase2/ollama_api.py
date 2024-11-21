import streamlit as st
import ollama
from PIL import Image
import io

def analyze_image(uploaded_image):
    """
    Analyze the uploaded image using Ollama's Llama3.2-Vision model
    
    Args:
        uploaded_image: Uploaded image file
    
    Returns:
        str: Description of the image
    """
    try:
        # Convert uploaded file to bytes for Ollama
        image_bytes = uploaded_image.getvalue()
        
        # Call Ollama API
        response = ollama.chat(
            model='llama3.2-vision',
            messages=[{
                'role': 'user',
                'content': 'Describe this image in detail',
                'images': [image_bytes]
            }]
        )
        
        return response['message']['content']
    
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Ollama Vision Image Analyzer", 
        page_icon="🖼️", 
        layout="centered"
    )
    
    # Title and description
    st.title("🖼️ Ollama Vision Image Analyzer")
    st.write("Upload an image and get a detailed description using Llama3.2-Vision")
    
    # Image upload widget
    uploaded_image = st.file_uploader(
        "Choose an image", 
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Upload an image to analyze"
    )
    
    # Display and analyze image
    if uploaded_image is not None:
        # Display the uploaded image
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Analyze button
        if st.button("Analyze Image", type="primary"):
            with st.spinner("Analyzing image..."):
                description = analyze_image(uploaded_image)
                
                if description:
                    st.subheader("Image Description")
                    st.write(description)

# Run the app
if __name__ == "__main__":
    main()
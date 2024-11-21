import streamlit as st
from PIL import Image
from base64 import b64encode
import google.generativeai as genai

def encode_image(image):
    """
    Encode image bytes to base64 string.
    """
    return b64encode(image).decode('utf-8')

def extract_text_from_image(image, api_key):
    """
    Extract text from an image using Gemini 1.5 Flash model.
    """
    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Encode the image
    encoded_image = encode_image(image)
    
    # Create model instance
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prepare the prompt
    prompt = """
    Analyze this image and provide a detailed report including:
                    1. Type of scan/image
                    2. Key findings and observations
                    3. Notable anatomical structures
                    4. Any abnormalities or pathological findings
                    5. Potential diagnoses based on imaging features
                    6. Areas requiring attention or follow-up
                    7. Technical quality of the image
                    8. Recommendations for additional imaging if needed.

                    Then provide a summary using medical terms for disease and injuries name in 2-3 sentences.
    """
    
    # Create message parts
    message = [
        {
            "role": "user",
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": encoded_image
                    }
                }
            ]
        }
    ]
    
    # Generate response
    response = model.generate_content(message)
    return response.text

def clean_text(raw_text):
    """
    Clean the extracted text to remove unnecessary characters and format it.
    """
    # Remove asterisks and clean up extra spaces
    cleaned_text = raw_text.replace("***", "").strip()
    
    # Replace double newlines with a single newline for better formatting
    cleaned_text = cleaned_text.replace("\n\n", "\n")
    
    return cleaned_text

# Streamlit App
st.title("Medical Image Analysis")
st.write("This application analyzes medical images (e.g., CT or MRI scans) to extract and interpret key findings. The analysis is powered by Google's Gemini AI model.")
# page = st.selectbox("Choose and option",["Type of scan/image","Summary"])
# Input: Image File
uploaded_image = st.file_uploader("Upload a medical image (JPG, JPEG, or PNG)", type=["jpg", "jpeg", "png"])

# Fixed API key for simplicity
api_key = "AIzaSyCQrYGVRTNivr4Dh_xhJLkVovy6kDEFhKY"

# Process the image and extract text
if uploaded_image:
    try:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Read the image bytes
        image_bytes = uploaded_image.read()
        
        # Extract and clean text
        st.write("### Processing the image...")
        extracted_text = extract_text_from_image(image_bytes, api_key)
        cleaned_text = clean_text(extracted_text)
        
        # Display the result
        st.subheader("Extracted and Analyzed Text:")
        sections = cleaned_text.split("\n\n")
        
        for section in sections:
            if section.strip().startswith("**"):
                st.markdown(f"### {section.strip()}")  # Subheading for sections
            else:
                st.write(section.strip())  # Regular text for content

        # if page == "Summary":
            # http://localhost:8501/#summary-using-medical-terms
    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Please upload a medical image to proceed.")

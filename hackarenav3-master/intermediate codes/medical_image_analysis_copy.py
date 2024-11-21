from PIL import Image
from base64 import b64encode
import google.generativeai as genai

def encode_image(image):
    """
    Encode image bytes to base64 string.
    """
    return b64encode(image).decode('utf-8')

def extract_text_from_image(image, api_key="AIzaSyCQrYGVRTNivr4Dh_xhJLkVovy6kDEFhKY"):
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
    ### Updated Prompt with Changes

"Analyze the given CT scan image and provide a detailed report, focusing on the detection and classification of Epidural Hematoma (EDH) and related conditions. Follow these steps systematically:

1. **Type of Scan/Image**: Confirm the imaging modality (e.g., non-contrast CT scan of the brain).  
2. **Key Findings and Observations**: Identify and describe notable features, including fractures, mass effects, or hyperdense regions.  
3. **Detection of EDH**: Look for a biconvex hyperdense area between the skull and dura mater, noting its location, size, and characteristics.  
4. **Classification of EDH (if present)**: Determine if the EDH is acute (hyperdense), subacute (isodense), or chronic (hypodense).  
5. **Notable Anatomical Structures**: Describe affected brain regions, midline shifts, ventricular compression, or herniation.  
6. **Abnormalities or Pathological Findings**: Highlight associated findings such as skull fractures, vascular injuries, or bleeding.  
7. **Hematoma Measurements**: Provide thickness (mm), volume (mL), and extent of compression or displacement.  
8. **Potential Diagnoses Based on Imaging**: State whether EDH is present or not and, if so, its type and severity.  
9. **Areas Requiring Attention or Follow-Up**: Indicate urgent concerns, such as increased intracranial pressure or need for surgical intervention.  
10. **Technical Quality of the Image**: Assess image clarity and adequacy for diagnosis.  
11. **Recommendations for Additional Imaging**: Suggest further scans if needed to clarify findings.

**Summary**: Provide a concise conclusion, using medical terms, summarizing the presence or absence of EDH, its type, severity, and immediate recommendations in 2-3 sentences."
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

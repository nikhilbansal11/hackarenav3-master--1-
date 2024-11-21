from PIL import Image
from base64 import b64encode
import google.generativeai as genai
import re
import cv2
import requests
from io import BytesIO

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
    # prompt = """
    #     Segment the image into zones (e.g., white matter, ventricles, orbits) and describe the features and characteristics of each zone in detail

    #     Generate a formal medical report including:
    #         1. Clinical Findings
    #             which have Detailed description of observations and Anatomical structures involved in 2-3 sentences
    #         2. Impression
    #             Potential diagnoses
    #         3. Recommendations
    #             - Suggested follow-up studies and Clinical correlation recommendations
    #         4. Summary 
    #             (2-3 sentences using medical terms, disease name and observations like this 
    #             example-1 "Minor small vessel ischaemic disease of the deep white matter is noted. Otherwise normal CT head."
    #             example-2 "CT Brain study is within normal limits.") 
    #             If any disease if there then mention the disease name.
    #         Format the report professionally using standard medical reporting structure and terminology 
    # """

    prompt = """"
        Analyze the given CT/MRI/X-ray image and provide a detailed description and report. 
        Begin by analyzing the visual structure, patterns, and highlights, focusing on features 
        such as density, contrast, anatomical landmarks, and any structural abnormalities. 
        Identify and describe specific anomalies, irregularities, or changes, including their 
        implications on anatomical structures and clinical conditions like ischemia, tumors, or 
        trauma. Compare the observed image with a standard healthy imaging reference, highlighting 
        deviations in structural or density features. Segment the image into zones 
        (e.g., white matter, ventricles, orbits) and provide a zone-specific description.

    Based on the image description, generate a structured medical
    report in standard format with sections like Clinical Information, Technique, 
    Findings, and Conclusion. Emphasize key findings, abnormalities, and their 
    clinical significance in the report. Highlight comparative differences between 
    the described image and standard healthy imaging to offer diagnostic clarity. 
    Additionally, provide a patient-friendly explanation summarizing the findings in simplified 
    language while maintaining clinical accuracy. Use a pre-designed report template with headings 
    such as Introduction, Findings, and Final Remarks to ensure a consistent and professional format.
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
    Clean the extracted text to remove unnecessary characters, format it, and print it clearly.
    """
    formatted_text = re.sub(r"(\d+\.\s)", r"\n\1", raw_text)

    # Remove unnecessary spaces or blank lines
    formatted_text = "\n".join(line.strip() for line in formatted_text.split("\n") if line.strip())

    # Print the formatted text clearly
    print("Formatted Text:\n")
    print(formatted_text)
    return formatted_text

def clean_text_2(raw_text):
    

    # Make words between ** bold and remove the asterisks
    formatted_text = re.sub(r"\*\*(.+?)\*\*", r"**\1**", raw_text)

    # Ensure dot points are aligned with content
    bullet_points_pattern = r"(?<!\n)- "  # Matches standalone bullet points
    formatted_text = re.sub(bullet_points_pattern, r"\n- ", formatted_text)

    # Add spacing after section headers for better readability
    section_pattern = r"(?<=\n)(\*\*.*?\*\*:)"
    formatted_text = re.sub(section_pattern, r"\n\1\n", formatted_text)

    # Fix spacing issues by ensuring no more than two consecutive newlines
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text.strip())

    # Ensure text is properly trimmed
    formatted_text = formatted_text.strip()

    return formatted_text


def process_image_from_path(image_path):
    """
    Processes an image from the given path.
    - Resizes the image to 256x256.
    - Converts it to grayscale.
    
    Args:
        image_path (str): Path to the image file.
    
    Returns:
        processed_image: Processed image in grayscale.
    """
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image not found or path is incorrect.")
        
        # Resize the image to 256x256
        resized_image = cv2.resize(image, (256, 256))
        
        # Convert the image to grayscale
        processed_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
        
        return processed_image
    except Exception as e:
        print(f"Error processing the image: {e}")
        return None


def show_image_from_url(image_url):
    """
    Fetches an image from the web using the provided URL and displays it.
    
    Args:
        image_url (str): The URL of the image.
    
    Returns:
        None
    """
    try:
        # Send a GET request to fetch the image
        response = requests.get(image_url)
        
        # Ensure the request was successful
        if response.status_code == 200:
            # Open the image from the content of the response
            image = Image.open(BytesIO(response.content))
            
            # Show the image
            return image
        else:
            print(f"Error: Unable to fetch image. HTTP status code {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

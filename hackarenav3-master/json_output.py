import re
import json

def parse_medical_text_to_json(text):
    # Define the keys and corresponding regex patterns
    patterns = {
        "disease name": r"\*\*Disease Name:\*\*\s*(.+?)\n",
        "clinical findings": r"\*\*1\. Clinical Findings:\*\*\n([\s\S]*?)\n\n",
        "impression": r"\*\*2\. Impression:\*\*\n([\s\S]*?)\n\n",
        "recommendations": r"\*\*3\. Recommendations:\*\*\n([\s\S]*?)\n\n",
        "summary": r"\*\*4\. Summary:\*\*\n([\s\S]*?)\nTERMINATE"
    }
    
    # Parse the text using regex patterns
    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parsed_data[key] = match.group(1).strip()
    
    return json.dumps(parsed_data, indent=4)
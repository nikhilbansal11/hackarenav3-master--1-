from flask import Flask, request, jsonify, send_file
from datetime import datetime
from io import BytesIO
import os

# Import necessary components
from PIL import Image
from medical_image_analyzer import extract_text_from_image, clean_text
from image_processing import MedicalImageAnalyzer
from report_gen import save_report
from flask_cors import CORS
from  json_output import parse_medical_text_to_json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the analyzer
analyzer = MedicalImageAnalyzer()
report = ""
# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Endpoint to analyze a medical image.
    """
    try:
        analysis_type = request.form.get("analysis_type", "Simple Description")
        file = request.files.get("file")  # Ensure the field name matches in the frontend
        
        if not file:
            return jsonify({"error": "No image file provided"}), 400
        
        image = Image.open(file)
        with BytesIO() as img_byte_arr:
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            extracted_text = extract_text_from_image(img_byte_arr.read())
            cleaned_text = clean_text(extracted_text)
        
        if not cleaned_text:
            return jsonify({"error": "Failed to extract text from the image"}), 500

        # Generate report
        report = analyzer.generate_report(cleaned_text)
        json_output = parse_medical_text_to_json(report)

        if not report:
            return jsonify({"error": "Failed to generate report"}), 500

        # Save the report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
        if save_report(report, filename):
            return jsonify({
                "message": "Report generated and saved successfully", 
                "filename": filename, 
                "report": report
            })
        else:
            return jsonify({"error": "Failed to save report"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/json_output', methods=['POST'])
def get_json_output():
    """
    Endpoint to extract and return JSON output from a medical image.
    """
    try:
        # file = request.files.get("file")  # Ensure the field name matches in the frontend

        # if not file:
        #     return jsonify({"error": "No image file provided"}), 400

        # image = Image.open(file)
        # with BytesIO() as img_byte_arr:
        #     image.save(img_byte_arr, format='PNG')
        #     img_byte_arr.seek(0)
        #     extracted_text = extract_text_from_image(img_byte_arr.read())
        #     cleaned_text = clean_text(extracted_text)

        # if not cleaned_text:
        #     return jsonify({"error": "Failed to extract text from the image"}), 500

        # # Generate report
        # report = analyzer.generate_report(cleaned_text)
        json_output = parse_medical_text_to_json(report)
        print(json_output)

        if not json_output:
            return jsonify({"error": "Failed to generate JSON output"}), 500

        return jsonify({"json_output": json_output})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reports', methods=['GET'])
def get_reports():
    """
    Endpoint to fetch the list of reports.
    """
    try:
        if os.path.exists("reports"):
            reports = os.listdir("reports")
            print("c-------------",reports)
            return jsonify({"reports": reports})
        else:
            return jsonify({"message": "No reports directory found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_report(filename):
    """
    Endpoint to download a specific report.
    """
    try:
        filepath = os.path.join("reports", filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({"error": "Report not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/settings', methods=['POST'])
def update_settings():
    """
    Endpoint to update analysis settings.
    """
    try:
        detail_level = request.json.get("detail_level", "Standard")
        include_analysis = request.json.get("include_analysis", ["Clinical Findings"])
        report_format = request.json.get("report_format", "Standard")
        
        # Mock saving settings (replace with real logic if needed)
        settings = {
            "detail_level": detail_level,
            "include_analysis": include_analysis,
            "report_format": report_format
        }
        
        return jsonify({"message": "Settings updated successfully", "settings": settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

from report_gen import save_report
from config import API_KEY
# from image_processing import MedicalImageAnalyzer
from image_processing_v2 import MedicalImageAnalyzer
from json_output import *
import streamlit as st
from PIL import Image
from medical_image_analyzer import extract_text_from_image, clean_text, process_image_from_path, show_image_from_url, clean_text_2
from datetime import datetime
import os
import io


def main():
    st.title("Medical Image Analysis System")
    
    analyzer = MedicalImageAnalyzer()
    
    page = st.sidebar.selectbox(
        "Select Operation",
        ["Image Analysis", "Report History", "Settings"]
    )
    
    if page == "Image Analysis":
        st.header("Upload Medical Image")
        
        # Add analysis type selector
        analysis_type = st.radio(
            "Select Analysis Type",
            ["Simple Description"]
        )
        
        # Add input method selector
        input_method = st.radio(
            "Select Input Method",
            ["File Upload", "Image Path"]
        )
        
        image = None
        
        if input_method == "File Upload":
            uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
        else:
            image_path = st.text_input("Enter the path to your image:")
            if image_path:
                image = show_image_from_url(image_path)
        
        if image is not None:
            try:
                st.image(image, caption="Input Image", use_column_width=True)
                
                analysis_container = st.container()
                report_container = st.container()
                with st.spinner("Processing Image"):

                    # Convert image to bytes before passing to extract_text_from_image
                    with io.BytesIO() as img_byte_arr:
                        image.save(img_byte_arr, format='PNG')  # Convert image to bytes
                        img_byte_arr.seek(0)  # Go to the start of the byte array
                        extracted_text = extract_text_from_image(img_byte_arr.read())  # Pass bytes to function
                        cleaned_text = clean_text_2(extracted_text)


                    # Show cleaned text (optional for user)
                    with analysis_container:
                        st.subheader("Extracted and Cleaned Text")
                        st.write(cleaned_text)


                if cleaned_text:
                    with st.spinner("Generating report..."):
                        report = analyzer.generate_report(cleaned_text)
                        
                        with report_container:
                            if report:
                                st.subheader("Generated Report")
                                st.markdown(report)
                                
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"report_{timestamp}.txt"
                                if save_report(report, filename):
                                    st.success(f"Report saved as {filename}")
                                    
                                    with open(f"reports/{filename}", "r", encoding='utf-8') as f:
                                        report_content = f.read()
                                    st.download_button(
                                        label="Download Report",
                                        data=report_content,
                                        file_name=filename,
                                        mime="text/plain"
                                    )
                            else:
                                st.error("Failed to generate report")
                else:
                    st.error("Failed to extract text from image")
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")


    elif page == "Report History":
        st.header("Previous Reports")
        if os.path.exists("reports"):
            reports = os.listdir("reports")
            if reports:
                selected_report = st.selectbox("Select a report to view", reports)
                try:
                    with open(f"reports/{selected_report}", "r", encoding='utf-8') as f:
                        report_content = f.read()
                        st.text_area("Report Content", report_content, height=400)
                        st.download_button(
                            label="Download Report",
                            data=report_content,
                            file_name=selected_report,
                            mime="text/plain"
                        )
                except Exception as e:
                    st.error(f"Error reading report: {str(e)}")
            else:
                st.info("No reports found")
        else:
            st.info("Reports directory not found")
    
    elif page == "Settings":
        st.header("Settings")
        st.subheader("Analysis Settings")
        
        detail_level = st.select_slider(
            "Analysis Detail Level",
            options=["Basic", "Standard", "Detailed", "Comprehensive"],
            value="Standard"
        )
        
        st.multiselect(
            "Include in Analysis",
            ["Clinical Findings", "Measurements", "Comparative Analysis", "Risk Factors"],
            default=["Clinical Findings"]
        )
        
        report_format = st.selectbox(
            "Report Format",
            ["Standard", "Detailed", "Summary Only"]
        )
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully")

    # Cleanup temporary files when the session ends
    if st.session_state.get('initialized'):
        analyzer.cleanup()
    else:
        st.session_state.initialized = True

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    main()

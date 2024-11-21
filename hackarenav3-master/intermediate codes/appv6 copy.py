import streamlit as st
import os
from PIL import Image
import io
from datetime import datetime
import tempfile
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
import base64
from medical_image_analysis import extract_text_from_image, clean_text  # Assuming these functions are defined

class MedicalImageAnalyzer:
    def __init__(self):
        self.config_list = [{
            "model": "gemini-1.5-flash",
            "api_key": "AIzaSyCQrYGVRTNivr4Dh_xhJLkVovy6kDEFhKY",
            "api_type": "google"
        }]
        
        self.assistant = AssistantAgent(
            "medical_assistant",
            llm_config={"config_list": self.config_list}
        )
        
        self.image_agent = MultimodalConversableAgent(
            "image_analyzer",
            llm_config={"config_list": self.config_list},
            max_consecutive_auto_reply=1
        )
        
        self.user_proxy = UserProxyAgent(
            "user_proxy",
            code_execution_config={"use_docker": False},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )

        # Create temp directory for image processing
        self.temp_dir = tempfile.mkdtemp()

    def generate_report(self, cleaned_text):
        """Generate comprehensive medical report based on cleaned text"""
        try:
            prompt = f"""Based on the following image analysis text:
            
            {cleaned_text or 'No analysis available'}
            
            Generate a formal medical report including:
            1. Clinical Findings
                which have Detailed description of observations and Anatomical structures involved in 2-3 sentences
            2. Impression
                Potential diagnoses
            3. Recommendations
                - Suggested follow-up studies and Clinical correlation recommendations
            4. Summary 
                (2-3 sentences using medical terms and observations)
            
            Format the report professionally using standard medical reporting structure and terminology ."""

            chat_response = self.user_proxy.initiate_chat(
                self.assistant,
                message=prompt
            )
            
            if hasattr(chat_response, 'chat_history') and chat_response.chat_history:
                last_message = chat_response.chat_history[-1]['content']
                return last_message
            return None
        except Exception as e:
            st.error(f"Error in report generation: {str(e)}")
            return None

    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            st.error(f"Error cleaning up temporary files: {str(e)}")

def save_report(report, filename):
    """Save the generated report to a file"""
    try:
        if report is None:
            raise ValueError("Report content is empty")
            
        report_content = str(report)
        
        with open(f"reports/{filename}", "w", encoding='utf-8') as f:
            f.write(report_content)
        return True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

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
            ["Simple Description", "Detailed Medical Analysis"]
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
                image = analyzer.process_image_from_path(image_path)
        
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
                        cleaned_text = clean_text(extracted_text)


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

                
                # with st.spinner("Processing image..."):
                #     # Extract text from the image
                #     extracted_text = extract_text_from_image(image)
                #     cleaned_text = clean_text(extracted_text)
                    
                #     # Show cleaned text (optional for user)
                #     with analysis_container:
                #         st.subheader("Extracted and Cleaned Text")
                #         st.write(cleaned_text)
                    
            #         if cleaned_text:
            #             with st.spinner("Generating report..."):
            #                 report = analyzer.generate_report(cleaned_text)
                            
            #                 with report_container:
            #                     if report:
            #                         st.subheader("Generated Report")
            #                         st.markdown(report)
                                    
            #                         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #                         filename = f"report_{timestamp}.txt"
            #                         if save_report(report, filename):
            #                             st.success(f"Report saved as {filename}")
                                        
            #                             with open(f"reports/{filename}", "r", encoding='utf-8') as f:
            #                                 report_content = f.read()
            #                             st.download_button(
            #                                 label="Download Report",
            #                                 data=report_content,
            #                                 file_name=filename,
            #                                 mime="text/plain"
            #                             )
            #                     else:
            #                         st.error("Failed to generate report")
            #         else:
            #             st.error("Failed to extract text from image")
            # except Exception as e:
            #     st.error(f"Error processing image: {str(e)}")

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

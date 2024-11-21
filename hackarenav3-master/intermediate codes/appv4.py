import streamlit as st
import os
from PIL import Image
import io
from datetime import datetime
import tempfile
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

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

    def save_temp_image(self, image):
        """Save uploaded image to temporary file and return path"""
        try:
            temp_path = os.path.join(self.temp_dir, "temp_image.png")
            image.save(temp_path)
            return temp_path
        except Exception as e:
            st.error(f"Error saving temporary image: {str(e)}")
            return None

    def analyze_image(self, image_path, analysis_type="simple"):
        print("A",image_path)
        result = ""
        for i in range(len(image_path)):
            result += str(i)
        # print("B",image_bytes)
        """Analyze image using specified type"""
        try:
            # Read the image file as bytes
            with open(image_path, 'rb') as img_file:
                image_bytes = img_file.read()

            # Create the prompt based on analysis type
            if analysis_type == "simple":
                prompt = """Describe what is in this image in 2 sentences?
                {result} """
            else:
                prompt = """Analyze this medical image and provide a detailed report including:
                1. Type of scan/image
                2. Key findings and observations
                3. Notable ana  tomical structures
                4. Any abnormalities or pathological findings
                5. Potential diagnoses based on imaging features
                6. Areas requiring attention or follow-up
                7. Technical quality of the image
                8. Recommendations for additional imaging if needed
                
                image: {}
                Please be thorough and use appropriate medical terminology in your analysis.""".format(image_path)

            chat_response = self.user_proxy.initiate_chat(
                self.image_agent,
                message=prompt, 
                # image=image_bytes  # Pass image as bytes
            )
            
            if hasattr(chat_response, 'chat_history') and chat_response.chat_history:
                last_message = chat_response.chat_history[-1]['content']
                return last_message
            return None
        except Exception as e:
            st.error(f"Error in image analysis: {str(e)}")
            return None

    def generate_report(self, image_analysis):
        """Generate comprehensive medical report"""
        try:
            prompt = f"""Based on the following image analysis:
            
            {image_analysis or 'No analysis available'}
            
            Generate a formal medical report including:
            1. Study Information
                - Type of examination
                - Date and time of analysis
            2. Clinical Findings
                - Detailed description of observations
                - Anatomical structures involved
            3. Impression
                - Summary of key findings
                - Potential diagnoses
            4. Recommendations
                - Suggested follow-up studies
                - Clinical correlation recommendations
            
            Format the report professionally using standard medical reporting structure and terminology."""

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
        
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                # Read and display the uploaded image
                image_bytes = uploaded_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                analysis_container = st.container()
                report_container = st.container()
                
                with st.spinner("Processing image..."):
                    # Save image to temporary file
                    image_path = analyzer.save_temp_image(image)
                    
                    if image_path:
                        with st.spinner("Analyzing image..."):
                            analysis_type_param = "simple" if analysis_type == "Simple Description" else "detailed"
                            analysis_result = analyzer.analyze_image(image_path, analysis_type_param)
                            
                            with analysis_container:
                                if analysis_result:
                                    st.subheader("Image Analysis")
                                    st.write(analysis_result)
                                    
                                    if analysis_type == "Detailed Medical Analysis":
                                        if st.button("Generate Report"):
                                            with st.spinner("Generating report..."):
                                                report = analyzer.generate_report(analysis_result)
                                                
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
                                    st.error("Image analysis failed")
                    else:
                        st.error("Failed to process uploaded image")
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
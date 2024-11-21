import streamlit as st
import os
from PIL import Image
import pytesseract
import pandas as pd
from datetime import datetime
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

class MedicalImageAnalyzer:
    def __init__(self):
        # Initialize config for LLM
        self.config_list = [{
            "model": "gemini-1.5-flash",
            "api_key": "AIzaSyCQrYGVRTNivr4Dh_xhJLkVovy6kDEFhKY",
            "api_type": "google"
        }]
        
        # Initialize agents
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

    # def extract_text_from_image(self, image):
    #     """Extract text from uploaded image using OCR"""
    #     try:
    #         text = pytesseract.image_to_string(image)
    #         return text
    #     except Exception as e:
    #         st.error(f"Error in text extraction: {str(e)}")
    #         return None

    def analyze_medical_image(self, image):
        """Analyze medical image using the image agent"""
        try:
            response = self.user_proxy.initiate_chat(
                self.image_agent,
                message=f"""Analyze this medical image and provide:
                1. Type of scan/image
                2. Key findings
                3. Potential diagnoses
                4. Areas of concern
                5. Recommendations for further testing if needed
                Please be thorough and specific in medical terminology.""",
                image=image
            )
            return response
        except Exception as e:
            st.error(f"Error in image analysis: {str(e)}")
            return None

    def generate_report(self, image_analysis):
        """Generate comprehensive medical report"""
        try:
            prompt = f"""Based on the following information:

            
            Image Analysis: {image_analysis}
            
            Generate a detailed medical report including:
            1. Patient Information (if available)
            2. Study Details
            3. Clinical Findings
            4. Impression
            5. Recommendations
            
            Format it professionally and include relevant medical terminology."""

            response = self.user_proxy.initiate_chat(
                self.assistant,
                message=prompt
            )
            return response
        except Exception as e:
            st.error(f"Error in report generation: {str(e)}")
            return None

def save_report(report, filename):
    """Save the generated report to a file"""
    try:
        with open(f"reports/{filename}", "w") as f:
            f.write(report)
        return True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

def main():
    st.title("Medical Image Analysis System")
    
    # Initialize analyzer
    analyzer = MedicalImageAnalyzer()
    
    # Create sidebar for navigation
    page = st.sidebar.selectbox(
        "Select Operation",
        ["Image Analysis", "Report History", "Settings"]
    )
    
    if page == "Image Analysis":
        st.header("Upload Medical Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            with st.spinner("Processing image..."):
                # Extract text from image
                # extracted_text = analyzer.extract_text_from_image(image)
                
                # if extracted_text:
                #     st.subheader("Extracted Text")
                #     st.text_area("OCR Result", extracted_text, height=150)
                
                # Analyze image
                analysis_result = analyzer.analyze_medical_image(image)
                
                if analysis_result:
                    st.subheader("Image Analysis")
                    st.write(analysis_result)
                
                # Generate report
                if st.button("Generate Report"):
                    report = analyzer.generate_report(analysis_result)
                    if report:
                        st.subheader("Generated Report")
                        st.markdown(report)
                        
                        # Save report
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"report_{timestamp}.txt"
                        if save_report(report, filename):
                            st.success(f"Report saved as {filename}")
    
    elif page == "Report History":
        st.header("Previous Reports")
        if os.path.exists("reports"):
            reports = os.listdir("reports")
            if reports:
                selected_report = st.selectbox("Select a report to view", reports)
                with open(f"reports/{selected_report}", "r") as f:
                    st.text_area("Report Content", f.read(), height=400)
            else:
                st.info("No reports found")
    
    elif page == "Settings":
        st.header("Settings")
        # st.subheader("OCR Settings")
        st.checkbox("Enable preprocessing", value=True)
        st.slider("Image Quality Threshold", 0, 100, 75)
        
        st.subheader("Analysis Settings")
        st.multiselect(
            "Include in Analysis",
            ["Clinical Findings", "Measurements", "Comparative Analysis", "Risk Factors"],
            default=["Clinical Findings"]
        )

if __name__ == "__main__":
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    main()
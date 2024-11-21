from datetime import datetime
import tempfile
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
import base64
from medical_image_analyzer import extract_text_from_image, clean_text  # Assuming these functions are defined
import streamlit as st
import cv2

class MedicalImageAnalyzer:
    def __init__(self):
        self.config_list = [  
            {
                "model": "gemini-1.5-flash",
                "api_key": "AIzaSyCQrYGVRTNivr4Dh_xhJLkVovy6kDEFhKY",
                "api_type": "google"
            }
        ]
        
        # Agents
        self.diagnosis_agent = AssistantAgent(
            "diagnosis_agent",
            llm_config={"config_list": self.config_list}
        )
        
        self.image_agent = MultimodalConversableAgent(
            "image_analyzer",
            llm_config={"config_list": self.config_list},
            max_consecutive_auto_reply=1
        )
        
        self.verification_agent = AssistantAgent(
            "verification_agent",
            llm_config={"config_list": self.config_list}
        )
        
        self.approval_agent = AssistantAgent(
            "approval_agent",
            llm_config={"config_list": self.config_list}
        )
        
        self.user_proxy = UserProxyAgent(
            "user_proxy",
            code_execution_config={"use_docker": False},
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0
        )

        # Temporary directory for image processing
        self.temp_dir = tempfile.mkdtemp()

    def generate_report(self, cleaned_text):
        """Generate and verify medical report based on cleaned text."""
        try:
            # Step 1: Diagnosis by the Diagnosis Agent
            diagnosis_prompt = f"""Analyze the following medical text and provide a detailed diagnosis:
            
            {cleaned_text or 'No analysis available'}
            
            Include:
            - Detailed observations
            - Possible diagnoses with reasoning
            - Anatomical structures involved.
            
            Never write any code """
            
            diagnosis_response = self.user_proxy.initiate_chat(
                self.diagnosis_agent,
                message=diagnosis_prompt
            )
            diagnosis_text = (
                diagnosis_response.chat_history[-1]['content'] 
                if hasattr(diagnosis_response, 'chat_history') 
                else None
            )
            
            # Step 4: Generate final medical report
            report_prompt = f"""Generate a formal medical report based on the diagnosis:
                
                Diagnosis: {diagnosis_text or 'No diagnosis available'}
                
                Follow this structure:
                   Disease Name
                1. Clinical Findings
                2. Impression
                3. Recommendations
                4. Summary (2-3 sentences using medical terminology).
                Do not say that it is a template and "Since I cannot access or process real medical reports due to patient privacy concerns, I will generate a sample formal medical report based on the previously described sample neuroimaging report. Remember, this is for illustrative purposes only and should not be used for actual clinical diagnosis. A qualified physician must interpret medical images and generate a real medical report."
                """
                
            report_response = self.user_proxy.initiate_chat(
                self.diagnosis_agent,
                message=report_prompt
            )
            final_report = (
                report_response.chat_history[-1]['content'] 
                if hasattr(report_response, 'chat_history') 
                else None
            )
            return final_report
        
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

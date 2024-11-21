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
                (2-3 sentences using medical terms, disease name and observations like this 
                example-1 "Minor small vessel ischaemic disease of the deep white matter is noted. Otherwise normal CT head."
                example-2 "CT Brain study is within normal limits.") 
                If any disease if there then mention the disease name.
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



import os
import streamlit as st

def save_report(report, filename):
    try:
        if not report:
            raise ValueError("Report content is empty")
        os.makedirs("reports", exist_ok=True)
        with open(f"reports/{filename}", "w", encoding='utf-8') as f:
            f.write(report)
        return True
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return False

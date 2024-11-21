import streamlit as st
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
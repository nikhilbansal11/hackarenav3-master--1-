import streamlit as st
import requests
import io

def generate_medical_report(patient_data, image_file, logo_file):
    """
    Generate medical report by sending data to Flask backend
    """
    # Prepare the data for the request
    files = {
        'image': ('medical_image.png', image_file, 'image/png'),
        'logo': ('logo.png', logo_file, 'image/png')
    }
    
    data = {
        'json_content': {
            'patient_name': patient_data['name'],
            'patient_id': patient_data['id'],
            'patient_address': patient_data['address'],
            'patient_contact': patient_data['contact'],
            'symptoms': patient_data['symptoms'],
            'medical_terms': patient_data['medical_terms'],
            'clinical_findings': patient_data['clinical_findings'],
            'recommendations': patient_data['recommendations']
        }
    }
    
    try:
        # Send request to Flask backend
        response = requests.post(
            'http://localhost:5000/generate_report', 
            json=data, 
            files=files
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error generating report: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Drlogy Medical Report Generator",
        page_icon="🏥",
        layout="centered"
    )

    st.title("🏥 Drlogy Medical Report Generator")
    st.write("Generate comprehensive medical reports quickly and easily")

    # Patient Information Section
    st.header("📋 Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name")
        patient_id = st.text_input("Patient ID")
    
    with col2:
        patient_address = st.text_input("Patient Address")
        patient_contact = st.text_input("Patient Contact")

    # Medical Information Section
    st.header("📝 Medical Details")
    symptoms = st.text_area("Symptoms")
    medical_terms = st.text_area("Medical Terms")
    clinical_findings = st.text_area("Clinical Findings")
    recommendations = st.text_area("Recommendations")

    # File Uploads
    st.header("📂 Upload Files")
    medical_image = st.file_uploader("Upload Medical Image", type=['png', 'jpg', 'jpeg'])
    logo_image = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])

    # Generate Report Button
    if st.button("Generate Medical Report 📄"):
        # Validate inputs
        if not all([patient_name, patient_id, patient_address, patient_contact, 
                    symptoms, medical_terms, clinical_findings, 
                    recommendations, medical_image, logo_image]):
            st.warning("Please fill in all fields and upload required files")
        else:
            # Prepare patient data
            patient_data = {
                'name': patient_name,
                'id': patient_id,
                'address': patient_address,
                'contact': patient_contact,
                'symptoms': symptoms,
                'medical_terms': medical_terms,
                'clinical_findings': clinical_findings,
                'recommendations': recommendations
            }

            # Generate report
            report = generate_medical_report(
                patient_data, 
                medical_image, 
                logo_image
            )

            if report:
                st.success("Report generated successfully!")
                st.download_button(
                    label="Download Medical Report 📥",
                    data=report,
                    file_name="medical_report.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
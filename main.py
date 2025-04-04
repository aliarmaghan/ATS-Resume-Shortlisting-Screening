# streamlit_app/main.py

import streamlit as st
from drive_utils import authenticate_drive, list_folders, list_pdfs_in_folder, download_pdf
import requests
import os

st.set_page_config(page_title="ATS Resume Shortlister", layout="wide")
st.title("📂 ATS Resume Shortlister - Google Drive Edition")

# Step 1: Authenticate
if 'drive_service' not in st.session_state:
    st.info("🔐 Please authenticate with your Google Account to access your Drive")
    if st.button("🔓 Authenticate with Google"):
        st.session_state.drive_service = authenticate_drive()
        st.success("✅ Authenticated successfully!")

# Step 2: Browse folders
if 'drive_service' in st.session_state:
    folders = list_folders(st.session_state.drive_service)
    folder_options = {f['name']: f['id'] for f in folders}

    st.markdown("### 📁 Select a folder in your Drive:")
    selected_folder = st.selectbox("Choose a folder", list(folder_options.keys()))

    if selected_folder:
        folder_id = folder_options[selected_folder]
        pdf_files = list_pdfs_in_folder(st.session_state.drive_service, folder_id)

        if not pdf_files:
            st.warning("No PDFs found in this folder.")
        else:
            st.markdown("### 📑 Found Resumes:")
            for f in pdf_files:
                st.write(f"📄 {f['name']}")

            jd = st.text_area("Paste Job Description Here")

            if jd and st.button("🚀 Rank Resumes"):
                st.info("Downloading resumes and sending to n8n...")
                results = []
                for f in pdf_files:
                    download_pdf(st.session_state.drive_service, f['id'], f['name'])
                    with open(f"resumes/{f['name']}", "rb") as resume_file:
                        response = requests.post(
                            "https://mdali.app.n8n.cloud/webhook/resume-screening",  # Your n8n webhook
                            files={"file": (f['name'], resume_file, "application/pdf")},
                            data={"job_description": jd}
                        )
                        try:
                            output = response.json()
                        except:
                            output = {"error": "Invalid response from n8n"}
                        results.append((f['name'], output))

                st.success("✅ Ranking Complete!")

                for name, res in results:
                    st.subheader(name)
                    if "score" in res:
                        st.write(f"**Score:** {res['score']}/10")
                        st.write(f"**Why:** {res['justification']}")
                    else:
                        st.error("Failed to fetch score.")

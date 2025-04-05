import os
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import streamlit as st
from google.oauth2.service_account import Credentials

# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# def authenticate_drive():
#     flow = InstalledAppFlow.from_client_secrets_file(
#         'client_secrets.json', SCOPES
#     )

#     creds = flow.run_local_server(port=0)
#     service = build('drive', 'v3', credentials=creds)
#     return service

# import streamlit as st
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# def authenticate_drive():
#     # Load credentials from Streamlit secrets
#     credentials_info = {
#         "installed": {
#             "client_id": st.secrets["installed"]["client_id"],
#             "project_id": st.secrets["installed"]["project_id"],
#             "auth_uri": st.secrets["installed"]["auth_uri"],
#             "token_uri": st.secrets["installed"]["token_uri"],
#             "auth_provider_x509_cert_url": st.secrets["installed"]["auth_provider_x509_cert_url"],
#             "client_secret": st.secrets["installed"]["client_secret"],
#             "redirect_uris": st.secrets["installed"]["redirect_uris"]
#         }
#     }

#     # Create OAuth flow
#     flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)
#     creds = flow.run_console()

#     # Build the service
#     service = build('drive', 'v3', credentials=creds)
    
#     return service



import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive():
    # Extract credentials from Streamlit secrets
    credentials_info = {
        "installed": {
            "client_id": st.secrets["installed"]["client_id"],
            "project_id": st.secrets["installed"]["project_id"],
            "auth_uri": st.secrets["installed"]["auth_uri"],
            "token_uri": st.secrets["installed"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["installed"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["installed"]["client_secret"],
            "redirect_uris": st.secrets["installed"]["redirect_uris"]
        }
    }

    flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)

    if "credentials" not in st.session_state:
        creds = flow.run_console()  # ✅ Fix: Uses console-based auth instead of local server
        st.session_state["credentials"] = creds.to_json()  # Store in session state
    else:
        creds = Credentials.from_authorized_user_info(json.loads(st.session_state["credentials"]))

    service = build('drive', 'v3', credentials=creds)
    return service


def list_folders(service):
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id, name)"
    ).execute()
    return results.get('files', [])

def list_pdfs_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def download_pdf(service, file_id, filename, download_path='resumes/'):
    os.makedirs(download_path, exist_ok=True)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(os.path.join(download_path, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

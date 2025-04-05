import os
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import streamlit as st
from google.oauth2.service_account import Credentials
import webbrowser

# SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# def authenticate_drive():
#     flow = InstalledAppFlow.from_client_secrets_file(
#         'client_secrets.json', SCOPES
#     )
#     creds = flow.run_local_server(port=8501)
#     service = build('drive', 'v3', credentials=creds)
#     return service

# def authenticate_drive():
#     """Authenticate with Google Drive using credentials stored in Streamlit secrets"""
#     credentials_info = st.secrets["web"]  # ✅ Read from secrets
#     creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
#     service = build('drive', 'v3', credentials=creds)
#     return service

# # Register Google Chrome as the default browser (use correct Chrome path)
# webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"))

# # Define the scope(s) you need. Example below is for Drive read-only.
# SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# def authenticate_drive():
#     # Build a dictionary from st.secrets that matches the shape
#     # of your original client_secret.json
#     client_config = {
#         "web": {
#             "client_id": st.secrets["web"]["client_id"],
#             "project_id": st.secrets["web"]["project_id"],
#             "auth_uri": st.secrets["web"]["auth_uri"],
#             "token_uri": st.secrets["web"]["token_uri"],
#             "auth_provider_x509_cert_url": st.secrets["web"]["auth_provider_x509_cert_url"],
#             "client_secret": st.secrets["web"].get("client_secret", ""),
#             "redirect_uris": [
#                 # If your original JSON had multiple redirect URIs,
#                 # add them here. Example:
#                 "http://localhost"
#             ]
#         }
#     }

#     # Create the flow using the in-memory config
#     flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
#     # Run the local server flow to get credentials
#     creds = flow.run_local_server(port=0)
    
#     # Build the Drive service
#     service = build("drive", "v3", credentials=creds)
#     return service


import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

def authenticate_drive():
    service_account_info = {
        "type": st.secrets["TYPE"],
        "project_id": st.secrets["PROJECT_ID"],
        "private_key_id": st.secrets["PRIVATE_KEY_ID"],
        "private_key": st.secrets["PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": st.secrets["CLIENT_EMAIL"],
        "client_id": st.secrets["CLIENT_ID"],
        "auth_uri": st.secrets["AUTH_URI"],
        "token_uri": st.secrets["TOKEN_URI"],
        "auth_provider_x509_cert_url": st.secrets["AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": st.secrets["CLIENT_X509_CERT_URL"]
    }

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)
    return drive_service



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

import os
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_drive():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', SCOPES
    )

    creds = flow.run_local_server(port=0)
    service = build('drive', 'v3', credentials=creds)
    return service

# # def authenticate_drive():
# #     """Authenticate with Google Drive using credentials stored in Streamlit secrets"""
# #     credentials_info = st.secrets["web"]  # ✅ Read from secrets
# #     creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
# #     service = build('drive', 'v3', credentials=creds)
# #     return service






# # import streamlit as st
# # from google.oauth2 import service_account
# # from googleapiclient.discovery import build

# # def authenticate_drive():
# #     service_account_info = {
# #         "type": st.secrets["type"],
# #         "project_id": st.secrets["project_id"],
# #         "private_key_id": st.secrets["private_key_id"],
# #         "private_key": st.secrets["private_key"].replace("\\n", "\n"),
# #         "client_email": st.secrets["client_email"],
# #         "client_id": st.secrets["client_id"],
# #         "auth_uri": st.secrets["auth_uri"],
# #         "token_uri": st.secrets["token_uri"],
# #         "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
# #         "client_x509_cert_url": st.secrets["client_x509_cert_url"]
# #     }

# #     creds = service_account.Credentials.from_service_account_info(
# #         service_account_info,
# #         scopes=["https://www.googleapis.com/auth/drive.readonly"]
# #     )
# #     drive_service = build("drive", "v3", credentials=creds)
# #     return drive_service





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

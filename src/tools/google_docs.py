import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from agno.tools import Toolkit

class GoogleDocsTools(Toolkit):
    def __init__(self):
        super().__init__(name="google_docs_tools")
        self.register(self.post_to_google_doc)

    def post_to_google_doc(self, title: str, content: str) -> str:
        """
        Create a new Google Doc with the specified title and content, and return the document URL.
        Use this tool when you need to output your generated report to the user's Google Docs.
        The title format should be 'YYYY-MM-DD: [first name] - Daily Astrology & Tarot Report' if relevant.
        """
        SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']
        
        creds = None
        # Priority: Env Var, then Default Path
        service_account_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not service_account_path or not os.path.exists(service_account_path):
             service_account_path = 'secrets/service_account.json'
        
        if os.path.exists(service_account_path):
            creds = service_account.Credentials.from_service_account_file(
                service_account_path, scopes=SCOPES)
        else:
            current_env = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'NOT_SET')
            return f"Error: Strict Headless Authentication required. Credentials not found at '{service_account_path}' (Env Var: {current_env}). Interactive OAuth is disabled for security."

        try:
            drive_service = build('drive', 'v3', credentials=creds)
            docs_service = build('docs', 'v1', credentials=creds)

            # Check if we should append to an existing document
            target_doc_id = os.getenv('GOOGLE_DOC_ID')
            
            if target_doc_id:
                document_id = target_doc_id
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Removed @now prefix as requested
                full_content = f"{timestamp}\n# {title}\n\n{content}\n\n---\n\n"
                
                requests = [
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': full_content
                        }
                    }
                ]
                docs_service.documents().batchUpdate(
                    documentId=document_id, body={'requests': requests}).execute()
            else:
                # Create a new document using Drive API
                doc_metadata = {
                    'name': title,
                    'mimeType': 'application/vnd.google-apps.document'
                }
                file_metadata = drive_service.files().create(body=doc_metadata, fields='id').execute()
                document_id = file_metadata.get('id')
                
                # Insert text into the document
                requests = [
                    {
                        'insertText': {
                            'location': {'index': 1},
                            'text': content
                        }
                    }
                ]
                docs_service.documents().batchUpdate(
                    documentId=document_id, body={'requests': requests}).execute()

            # Share/Update permissions (mostly for new docs, but harmless for existing)
            user_email = os.getenv('USER_EMAIL')
            if user_email:
                try:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': user_email
                    }
                    drive_service.permissions().create(
                        fileId=document_id,
                        body=permission,
                        fields='id'
                    ).execute()
                except Exception as share_error:
                    # If already shared, this might 403, which is fine
                    if "already" not in str(share_error).lower():
                        print(f"Warning: Could not ensure sharing with {user_email}: {str(share_error)}")
                
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
            res_msg = f"Successfully updated Google Doc."
            if not target_doc_id:
                res_msg = f"Successfully created Google Doc '{title}'."
            
            if user_email:
                res_msg += f" Shared with {user_email}."
            res_msg += f" URL: {doc_url}"
            return res_msg
        
        except Exception as e:
            error_msg = str(e)
            if "not have permission" in error_msg or "403" in error_msg:
                return f"Error: Permission Denied (403). Possible reasons:\n1. Google Docs/Drive API are not enabled for this project.\n2. The Service Account lacks the 'Editor' role.\nDetailed error: {error_msg}"
            return f"Error creating Google Doc: {error_msg}"

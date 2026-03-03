import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
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
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    return "Error: credentials.json not found. The user needs to supply OAuth 2.0 client credentials (credentials.json) in the project root."
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            drive_service = build('drive', 'v3', credentials=creds)
            docs_service = build('docs', 'v1', credentials=creds)

            # Create a new document in Drive
            doc_metadata = {'name': title}
            document = docs_service.documents().create(body=doc_metadata).execute()
            document_id = document.get('documentId')

            # Insert text into the document
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content
                    }
                }
            ]
            docs_service.documents().batchUpdate(
                documentId=document_id, body={'requests': requests}).execute()
                
            doc_url = f"https://docs.google.com/document/d/{document_id}/edit"
            return f"Successfully created Google Doc '{title}'. URL: {doc_url}"
        
        except Exception as e:
            return f"Error creating Google Doc: {str(e)}"

import pickle
import os
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE, IS_PRODUCTION

class GoogleSheetsService:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Sheets API using OAuth2"""
        creds = None
        
        # Production mode (Railway) - use environment variables
        if IS_PRODUCTION:
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            refresh_token = os.getenv('GOOGLE_REFRESH_TOKEN')
            
            if not all([client_id, client_secret]):
                raise ValueError(
                    "Missing Google OAuth2 environment variables in production!\n"
                    "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in Railway."
                )
            
            if refresh_token:
                # Use existing refresh token
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=SCOPES
                )
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh token: {e}")
                    creds = None
            
            if not creds:
                # Need to generate new refresh token
                print("⚠️  No valid refresh token found!")
                print("You need to run this locally first to generate a refresh token.")
                print("Run: python generate_refresh_token.py")
                raise ValueError("Missing valid refresh token for production")
        
        # Development mode (local) - use credentials file
        else:
            # Check if we have saved credentials
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_FILE):
                        raise FileNotFoundError(
                            f"Please download your OAuth2 credentials from Google Cloud Console "
                            f"and save them as '{CREDENTIALS_FILE}' in the project directory.\n"
                            f"Instructions:\n"
                            f"1. Go to https://console.cloud.google.com/\n"
                            f"2. Select your project\n"
                            f"3. Go to 'APIs & Services' > 'Credentials'\n"
                            f"4. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'\n"
                            f"5. Choose 'Desktop application'\n"
                            f"6. Download the JSON file and rename it to '{CREDENTIALS_FILE}'"
                        )
                    
                    # Use standard desktop application flow
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def get_sheet_data(self, sheet_id, sheet_name, range_name='A:Z'):
        """Get all data from a specific sheet"""
        try:
            range_str = f'{sheet_name}!{range_name}'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id, 
                range=range_str
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"Error getting sheet data: {e}")
            return []
    
    def get_last_row_count(self, sheet_id, sheet_name):
        """Get the number of rows in the sheet"""
        try:
            range_str = f'{sheet_name}!A:A'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id, 
                range=range_str
            ).execute()
            values = result.get('values', [])
            return len(values)
        except Exception as e:
            print(f"Error getting row count: {e}")
            return 0

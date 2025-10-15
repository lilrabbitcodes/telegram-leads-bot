#!/usr/bin/env python3
"""
Generate refresh token for Railway deployment
Run this locally to get the refresh token needed for production
"""

import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SCOPES, CREDENTIALS_FILE

def generate_refresh_token():
    """Generate a refresh token for production use"""
    print("=" * 60)
    print("GENERATING REFRESH TOKEN FOR RAILWAY")
    print("=" * 60)
    print()
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: {CREDENTIALS_FILE} not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Select your project")
        print("3. Enable Google Sheets API")
        print("4. Go to 'APIs & Services' > 'Credentials'")
        print("5. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
        print("6. Choose 'Desktop application'")
        print("7. Download the JSON file and rename it to 'credentials.json'")
        return
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save token locally (for backup)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)
        
        # Extract values for Railway
        print("✅ Authentication successful!")
        print()
        print("📋 ADD THESE TO RAILWAY ENVIRONMENT VARIABLES:")
        print("-" * 50)
        print(f"GOOGLE_CLIENT_ID={creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print()
        print("📋 ALSO ADD THESE (if not already set):")
        print("-" * 50)
        print("TELEGRAM_BOT_TOKEN=8456182596:AAG4OBD_MzL6twCmG_uRx_EKQiEr7PT_A3A")
        print("TELEGRAM_ALLOWED_USERS=YOUR_USER_ID_HERE")
        print("GOOGLE_SHEET_ID=14bxGTo91qif2XRw7nmLpcjliNSSWw3tZXKwyeJir5lM")
        print("GOOGLE_SHEET_TAB=facebook")
        print("CHECK_INTERVAL_MINUTES=5")
        print()
        print("⚠️  IMPORTANT:")
        print("- Copy these values EXACTLY as shown")
        print("- Don't include quotes around the values")
        print("- The refresh token will allow Railway to access your sheets")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import os
    generate_refresh_token()

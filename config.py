import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8456182596:AAG4OBD_MzL6twCmG_uRx_EKQiEr7PT_A3A')
TELEGRAM_ALLOWED_USERS = [int(user_id) for user_id in os.getenv('TELEGRAM_ALLOWED_USERS', '7027631325').split(',') if user_id.strip()]

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '14bxGTo91qif2XRw7nmLpcjliNSSWw3tZXKwyeJir5lM')
GOOGLE_SHEET_TAB = os.getenv('GOOGLE_SHEET_TAB', 'facebook')

# Monitoring Configuration
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))

# OAuth2 Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Environment Detection
IS_PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.getenv('PORT') is not None

#!/usr/bin/env python3
"""
Tokyo Garden Clinic - Telegram Leads Bot (All-in-One)
Monitors Google Sheets for new leads and sends notifications via Telegram
"""

import asyncio
import pickle
import os
import json
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from telegram import Bot
from telegram.error import TelegramError

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8456182596:AAG4OBD_MzL6twCmG_uRx_EKQiEr7PT_A3A')
TELEGRAM_ALLOWED_USERS = [int(user_id) for user_id in os.getenv('TELEGRAM_ALLOWED_USERS', '7027631325').split(',') if user_id.strip()]
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '14bxGTo91qif2XRw7nmLpcjliNSSWw3tZXKwyeJir5lM')
GOOGLE_SHEET_TAB = os.getenv('GOOGLE_SHEET_TAB', 'facebook')
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
IS_PRODUCTION = os.getenv('RAILWAY_ENVIRONMENT') is not None or os.getenv('PORT') is not None

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
                print("⚠️  No valid refresh token found!")
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
                            f"and save them as '{CREDENTIALS_FILE}' in the project directory."
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

class TelegramService:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.allowed_users = TELEGRAM_ALLOWED_USERS
    
    async def send_notification(self, user_id, message):
        """Send a notification to a specific user"""
        if user_id not in self.allowed_users:
            print(f"User {user_id} is not authorized to receive notifications")
            return False
        
        try:
            await self.bot.send_message(chat_id=user_id, text=message)
            print(f"Notification sent to user {user_id}")
            return True
        except TelegramError as e:
            print(f"Error sending notification to user {user_id}: {e}")
            return False
    
    async def send_notifications_to_all(self, message):
        """Send notification to all allowed users"""
        tasks = []
        for user_id in self.allowed_users:
            tasks.append(self.send_notification(user_id, message))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return all(result for result in results if not isinstance(result, Exception))
        return False
    
    async def get_bot_info(self):
        """Get bot information"""
        try:
            bot_info = await self.bot.get_me()
            return bot_info
        except TelegramError as e:
            print(f"Error getting bot info: {e}")
            return None

class LeadsMonitor:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.telegram_service = TelegramService()
        self.last_row_count = 0
        self.initialized = False
    
    async def initialize(self):
        """Initialize the monitor by getting the current row count"""
        try:
            self.last_row_count = self.sheets_service.get_last_row_count(GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB)
            print(f"Initialized with {self.last_row_count} rows in sheet")
            self.initialized = True
        except Exception as e:
            print(f"Error initializing monitor: {e}")
            self.initialized = False
    
    def format_lead_notification(self, new_rows):
        """Format the notification message for new leads"""
        if not new_rows:
            return ""
        
        message = f"🆕 New Lead(s) Added to {GOOGLE_SHEET_TAB.title()} Sheet!\n\n"
        
        for i, row in enumerate(new_rows, 1):
            message += f"📋 Lead #{i}:\n"
            message += "=" * 30 + "\n"
            
            # Map actual columns from your Google Sheet
            field_mapping = {
                0: "📝 Form Type",
                1: "📅 Submission Date", 
                2: "👤 Name",
                3: "📧 Email",
                4: "📱 Phone",
                5: "🌐 Platform",
                6: "📢 Campaign Name",
                7: "🎯 Adset Name",
                8: "📺 Ad Name",
                9: "💪 Underarm Concerns",
                10: "👁️ Eye Area Concerns",
                11: "⏰ Duration of Concern",
                12: "📅 Preferred Appointment Time",
                13: "📞 Contact Preference",
                14: "📊 Status"
            }
            
            # Display key information first
            key_fields = [2, 3, 4, 1, 5, 14]  # Name, Email, Phone, Date, Platform, Status
            
            for j in key_fields:
                if j < len(row) and row[j] and str(row[j]).strip():
                    field_name = field_mapping.get(j, f"Field {j+1}")
                    message += f"{field_name}: {row[j]}\n"
            
            message += "\n📋 Additional Details:\n"
            message += "-" * 20 + "\n"
            
            # Display additional details
            additional_fields = [0, 6, 7, 8, 9, 10, 11, 12, 13]
            
            for j in additional_fields:
                if j < len(row) and row[j] and str(row[j]).strip():
                    field_name = field_mapping.get(j, f"Field {j+1}")
                    # Truncate very long fields
                    value = str(row[j])
                    if len(value) > 100:
                        value = value[:97] + "..."
                    message += f"{field_name}: {value}\n"
            
            message += "\n" + "=" * 40 + "\n\n"
        
        message += f"📊 Total leads in sheet: {self.last_row_count}\n"
        message += f"⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    def format_single_lead_notification(self, row, lead_number):
        """Format notification for a single lead"""
        if not row:
            return ""
        
        message = f"🆕 New Lead #{lead_number} Added to {GOOGLE_SHEET_TAB.title()} Sheet!\n\n"
        message += "📋 Lead Details:\n"
        message += "=" * 30 + "\n"
        
        # Map actual columns from your Google Sheet
        field_mapping = {
            0: "📝 Form Type",
            1: "📅 Submission Date", 
            2: "👤 Name",
            3: "📧 Email",
            4: "📱 Phone",
            5: "🌐 Platform",
            6: "📢 Campaign Name",
            7: "🎯 Adset Name",
            8: "📺 Ad Name",
            9: "💪 Underarm Concerns",
            10: "👁️ Eye Area Concerns",
            11: "⏰ Duration of Concern",
            12: "📅 Preferred Appointment Time",
            13: "📞 Contact Preference",
            14: "📊 Status"
        }
        
        # Display key information first
        key_fields = [2, 3, 4, 1, 5, 14]  # Name, Email, Phone, Date, Platform, Status
        
        for j in key_fields:
            if j < len(row) and row[j] and str(row[j]).strip():
                field_name = field_mapping.get(j, f"Field {j+1}")
                message += f"{field_name}: {row[j]}\n"
        
        message += "\n📋 Additional Details:\n"
        message += "-" * 20 + "\n"
        
        # Display additional details
        additional_fields = [0, 6, 7, 8, 9, 10, 11, 12, 13]
        
        for j in additional_fields:
            if j < len(row) and row[j] and str(row[j]).strip():
                field_name = field_mapping.get(j, f"Field {j+1}")
                # Truncate very long fields
                value = str(row[j])
                if len(value) > 100:
                    value = value[:97] + "..."
                message += f"{field_name}: {value}\n"
        
        message += "\n" + "=" * 40 + "\n"
        message += f"📊 Total leads in sheet: {self.last_row_count + lead_number}\n"
        message += f"⏰ Received at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    async def check_for_new_leads(self):
        """Check for new leads and send notifications"""
        if not self.initialized:
            await self.initialize()
            return
        
        try:
            current_row_count = self.sheets_service.get_last_row_count(GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB)
            
            if current_row_count > self.last_row_count:
                new_row_count = current_row_count - self.last_row_count
                print(f"Found {new_row_count} new row(s)!")
                
                # Get the new rows
                all_data = self.sheets_service.get_sheet_data(GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB)
                
                # Get only the new rows (skip header if exists)
                new_rows = all_data[self.last_row_count:]
                
                # Send individual notification for each new lead
                for i, new_row in enumerate(new_rows, 1):
                    notification = self.format_single_lead_notification(new_row, i)
                    
                    if notification:
                        success = await self.telegram_service.send_notifications_to_all(notification)
                        if success:
                            print(f"Individual notification sent for lead {i}!")
                        else:
                            print(f"Failed to send notification for lead {i}")
                        
                        # Small delay between notifications to avoid spam
                        await asyncio.sleep(1)
                
                # Update the row count
                self.last_row_count = current_row_count
            
            elif current_row_count < self.last_row_count:
                print(f"Row count decreased from {self.last_row_count} to {current_row_count}")
                self.last_row_count = current_row_count
            
        except Exception as e:
            print(f"Error checking for new leads: {e}")
    
    async def run_monitor(self):
        """Run the monitoring loop"""
        print(f"Starting leads monitor for sheet: {GOOGLE_SHEET_ID}")
        print(f"Monitoring tab: {GOOGLE_SHEET_TAB}")
        print(f"Check interval: {CHECK_INTERVAL_MINUTES} minutes")
        print(f"Allowed users: {self.telegram_service.allowed_users}")
        
        await self.initialize()
        
        if not self.initialized:
            print("Failed to initialize monitor. Exiting.")
            return
        
        while True:
            try:
                await self.check_for_new_leads()
                await asyncio.sleep(CHECK_INTERVAL_MINUTES * 60)
            except KeyboardInterrupt:
                print("\nMonitor stopped by user")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def test_telegram_connection():
    """Test the Telegram bot connection"""
    print("Testing Telegram bot connection...")
    
    telegram_service = TelegramService()
    bot_info = await telegram_service.get_bot_info()
    
    if bot_info:
        print(f"✅ Bot connected successfully!")
        print(f"Bot name: {bot_info.first_name}")
        print(f"Bot username: @{bot_info.username}")
        print(f"Bot ID: {bot_info.id}")
        print()
        
        if not TELEGRAM_ALLOWED_USERS:
            print("⚠️  No allowed users configured!")
            return False
        else:
            print(f"✅ Allowed users configured: {TELEGRAM_ALLOWED_USERS}")
            return True
    else:
        print("❌ Failed to connect to Telegram bot!")
        return False

async def main():
    """Main function"""
    print("=" * 60)
    print("Tokyo Garden Clinic - Telegram Leads Bot")
    print("=" * 60)
    
    # Test Telegram connection first
    if not await test_telegram_connection():
        print("Please fix the Telegram configuration before continuing.")
        return
    
    print("\nStarting leads monitoring...")
    print("Press Ctrl+C to stop the monitor")
    print("-" * 60)
    
    # Start monitoring
    monitor = LeadsMonitor()
    await monitor.run_monitor()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

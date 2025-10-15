import asyncio
import time
from datetime import datetime
from google_sheets_service import GoogleSheetsService
from telegram_service import TelegramService
from config import GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB, CHECK_INTERVAL_MINUTES

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
            
            # Map common lead fields (adjust based on your sheet structure)
            field_mapping = {
                0: "Name",
                1: "Email", 
                2: "Phone",
                3: "Source",
                4: "Message",
                5: "Date",
                6: "Status"
            }
            
            for j, cell_value in enumerate(row):
                field_name = field_mapping.get(j, f"Field {j+1}")
                if cell_value and str(cell_value).strip():
                    message += f"• {field_name}: {cell_value}\n"
            
            message += "\n"
        
        message += f"📊 Total rows in sheet: {self.last_row_count}"
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
                
                # Format and send notification
                notification = self.format_lead_notification(new_rows)
                
                if notification:
                    success = await self.telegram_service.send_notifications_to_all(notification)
                    if success:
                        print("Notifications sent successfully!")
                    else:
                        print("Failed to send some notifications")
                
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

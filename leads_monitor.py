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
        self.processed_leads = set()  # Track processed leads to avoid duplicates
    
    def get_lead_id(self, row):
        """Generate a unique ID for a lead based on name, email, and date"""
        if len(row) < 4:
            return None
        
        name = row[2] if len(row) > 2 else ""
        email = row[3] if len(row) > 3 else ""
        date = row[1] if len(row) > 1 else ""
        
        # Create a unique identifier
        return f"{name}_{email}_{date}".strip()
    
    async def initialize(self):
        """Initialize the monitor by getting the current row count"""
        try:
            self.last_row_count = self.sheets_service.get_last_row_count(GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB)
            
            # Load existing leads into processed set to avoid duplicate notifications
            all_data = self.sheets_service.get_sheet_data(GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB)
            for row in all_data[1:]:  # Skip header row
                lead_id = self.get_lead_id(row)
                if lead_id:
                    self.processed_leads.add(lead_id)
            
            print(f"Initialized with {self.last_row_count} rows in sheet")
            print(f"Loaded {len(self.processed_leads)} existing leads into memory")
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
    
    def is_new_lead(self, row):
        """Check if a lead is from October 16, 2025 onwards"""
        if len(row) < 2:
            return False
        
        try:
            # Get the submission date (column 1)
            submission_date_str = row[1]
            
            # Parse the date (format: "October 16 2025 14:00:15")
            from datetime import datetime
            submission_date = datetime.strptime(submission_date_str, "%B %d %Y %H:%M:%S")
            
            # Check if it's from October 16, 2025 onwards
            cutoff_date = datetime(2025, 10, 16, 0, 0, 0)
            return submission_date >= cutoff_date
            
        except Exception as e:
            print(f"Error parsing date '{row[1] if len(row) > 1 else 'N/A'}': {e}")
            return False
    
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
                
                # Filter for new leads from October 16, 2025 onwards that haven't been processed
                recent_leads = []
                for row in new_rows:
                    if self.is_new_lead(row):
                        lead_id = self.get_lead_id(row)
                        if lead_id and lead_id not in self.processed_leads:
                            recent_leads.append(row)
                            self.processed_leads.add(lead_id)  # Mark as processed
                
                if recent_leads:
                    print(f"Found {len(recent_leads)} NEW leads from October 16, 2025 onwards!")
                    
                    # Send individual notification for each recent lead
                    for i, recent_lead in enumerate(recent_leads, 1):
                        notification = self.format_single_lead_notification(recent_lead, i)
                        
                        if notification:
                            success = await self.telegram_service.send_notifications_to_all(notification)
                            if success:
                                print(f"Individual notification sent for recent lead {i}!")
                            else:
                                print(f"Failed to send notification for recent lead {i}")
                            
                            # Small delay between notifications to avoid spam
                            await asyncio.sleep(1)
                else:
                    print("No NEW leads from October 16, 2025 onwards found")
                
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

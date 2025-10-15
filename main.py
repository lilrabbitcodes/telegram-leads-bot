#!/usr/bin/env python3
"""
Tokyo Garden Clinic - Telegram Leads Bot
Monitors Google Sheets for new leads and sends notifications via Telegram
"""

import asyncio
import sys
from leads_monitor import LeadsMonitor
from telegram_service import TelegramService
from config import TELEGRAM_ALLOWED_USERS

async def test_telegram_connection():
    """Test the Telegram bot connection and get user IDs"""
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
            print("To get your Telegram user ID:")
            print("1. Send a message to your bot: @Tokyogardenclinic_leads_bot")
            print("2. The bot will show you your user ID")
            print("3. Add your user ID to the TELEGRAM_ALLOWED_USERS in config.py")
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
        sys.exit(1)
    
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
        sys.exit(1)

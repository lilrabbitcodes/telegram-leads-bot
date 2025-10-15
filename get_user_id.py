#!/usr/bin/env python3
"""
Helper script to get Telegram user IDs for configuring notifications
"""

import asyncio
from telegram_service import TelegramService

async def get_user_ids():
    """Get user IDs from recent bot interactions"""
    telegram_service = TelegramService()
    
    print("Getting user IDs from recent bot interactions...")
    print("Make sure someone has sent a message to your bot first!")
    print()
    
    try:
        bot = telegram_service.bot
        updates = await bot.get_updates()
        
        if not updates:
            print("❌ No recent messages found!")
            print("Please send a message to your bot: @Tokyogardenclinic_leads_bot")
            print("Then run this script again.")
            return
        
        print("✅ Found recent messages!")
        print()
        
        user_ids = set()
        for update in updates:
            if update.message:
                user = update.message.from_user
                user_ids.add(user.id)
                print(f"User ID: {user.id}")
                print(f"Name: {user.first_name} {user.last_name or ''}")
                print(f"Username: @{user.username or 'N/A'}")
                print("-" * 30)
        
        if user_ids:
            user_ids_list = list(user_ids)
            print(f"\n📋 User IDs to add to config:")
            print(f"TELEGRAM_ALLOWED_USERS = {user_ids_list}")
            print()
            print("Copy this line and add it to your config.py file!")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_user_ids())

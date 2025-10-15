import asyncio
from telegram import Bot
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_USERS

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
    
    async def get_user_chat_id(self, username=None):
        """Helper method to get user chat ID"""
        try:
            updates = await self.bot.get_updates()
            if updates:
                return updates[-1].message.from_user.id
        except TelegramError as e:
            print(f"Error getting updates: {e}")
        return None

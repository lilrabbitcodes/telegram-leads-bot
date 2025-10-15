# Tokyo Garden Clinic - Telegram Leads Bot

This bot monitors your Google Sheets for new leads and sends instant notifications via Telegram to authorized users only.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google OAuth2 Credentials

Since your organization blocks service account keys, we'll use OAuth2 instead:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create a new one)
3. **Enable Google Sheets API**:
   - Search for "Google Sheets API"
   - Click "ENABLE"
4. **Create OAuth2 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file
   - **Rename it to `credentials.json`** and place it in this folder

### 3. Configure Telegram Users

1. **Send a message to your bot**: @Tokyogardenclinic_leads_bot
2. **Get your user ID**:
   ```bash
   python get_user_id.py
   ```
3. **Update config.py** with your user ID:
   ```python
   TELEGRAM_ALLOWED_USERS = [123456789]  # Your user ID here
   ```

### 4. Run the Bot

```bash
python main.py
```

## 📋 Configuration

Edit `config.py` to customize:

- **GOOGLE_SHEET_ID**: Your Google Sheet ID
- **GOOGLE_SHEET_TAB**: Which tab to monitor (facebook, tiktok, whatsapp)
- **CHECK_INTERVAL_MINUTES**: How often to check for new leads
- **TELEGRAM_ALLOWED_USERS**: List of user IDs who can receive notifications

## 🔒 Security Features

- ✅ Only authorized Telegram users receive notifications
- ✅ Uses OAuth2 (no service account keys needed)
- ✅ Read-only access to Google Sheets
- ✅ Secure token storage

## 📱 How It Works

1. **Monitors your Google Sheet** every 5 minutes (configurable)
2. **Detects new rows** automatically
3. **Sends formatted notifications** to authorized Telegram users
4. **Includes all lead information** in the message

## 🛠️ Troubleshooting

### "credentials.json not found"

- Download OAuth2 credentials from Google Cloud Console
- Rename to `credentials.json` and place in project folder

### "No allowed users configured"

- Send a message to your bot first
- Run `python get_user_id.py` to get your user ID
- Add your user ID to `config.py`

### "Failed to connect to Telegram bot"

- Check your bot token in `config.py`
- Make sure the bot is active

## 📊 Notification Format

When a new lead is added, you'll receive:

```
🆕 New Lead(s) Added to Facebook Sheet!

📋 Lead #1:
• Name: John Doe
• Email: john@example.com
• Phone: +1234567890
• Source: Facebook Ad
• Message: Interested in consultation
• Date: 2024-01-15

📊 Total rows in sheet: 25
```

## 🚀 Running in Production

For continuous monitoring, you can:

- Run on a VPS/cloud server
- Use a process manager like PM2
- Set up as a systemd service
- Deploy to cloud platforms like Heroku or Railway

## 📞 Support

If you need help:

1. Check the troubleshooting section above
2. Verify all credentials are correct
3. Make sure your Google Sheet is accessible

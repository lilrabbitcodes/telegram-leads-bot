# 🚀 Railway Deployment Guide

Deploy your Telegram bot to Railway for **24/7 monitoring** of your Google Sheets!

## 📋 Prerequisites

1. **GitHub Account** (to store your code)
2. **Railway Account** (free tier available)
3. **Google Cloud Project** with Sheets API enabled

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Code for GitHub

1. **Initialize Git** (if not already done):

   ```bash
   cd "/Users/rebeccawan/Documents/Tokyo Garden Clinic/tele_agent"
   git init
   git add .
   git commit -m "Initial commit: Telegram leads bot"
   ```

2. **Create GitHub Repository**:

   - Go to https://github.com/new
   - Create a new repository (e.g., "telegram-leads-bot")
   - **Don't initialize with README** (you already have files)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/telegram-leads-bot.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Generate Refresh Token (Local)

1. **Get Google OAuth2 Credentials**:

   - Go to https://console.cloud.google.com/
   - Select your project
   - Enable Google Sheets API
   - Go to "APIs & Services" > "Credentials"
   - Create "OAuth 2.0 Client ID" (Desktop application)
   - Download JSON file → rename to `credentials.json`

2. **Generate Refresh Token**:
   ```bash
   python generate_refresh_token.py
   ```
   **Copy the output values!** You'll need them for Railway.

### Step 3: Deploy to Railway

1. **Go to Railway**: https://railway.app/
2. **Sign up/Login** with GitHub
3. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect Python and deploy

### Step 4: Configure Environment Variables

In Railway dashboard, go to your project → Variables tab:

**Add these environment variables:**

```
TELEGRAM_BOT_TOKEN=8456182596:AAG4OBD_MzL6twCmG_uRx_EKQiEr7PT_A3A
TELEGRAM_ALLOWED_USERS=YOUR_USER_ID_HERE
GOOGLE_SHEET_ID=14bxGTo91qif2XRw7nmLpcjliNSSWw3tZXKwyeJir5lM
GOOGLE_SHEET_TAB=facebook
CHECK_INTERVAL_MINUTES=5
GOOGLE_CLIENT_ID=your_client_id_from_refresh_token_script
GOOGLE_CLIENT_SECRET=your_client_secret_from_refresh_token_script
GOOGLE_REFRESH_TOKEN=your_refresh_token_from_refresh_token_script
```

**Replace `YOUR_USER_ID_HERE` with your actual Telegram user ID**

### Step 5: Deploy! 🎉

1. **Railway will automatically deploy** your bot
2. **Check the logs** to ensure it's running
3. **Test by adding a row** to your Google Sheet
4. **You should receive a Telegram notification!**

## ✅ What Happens Next

- **Bot runs 24/7** on Railway's servers
- **Monitors your Google Sheet** every 5 minutes
- **Sends notifications** when new leads are added
- **Never stops** (unless Railway service is down)
- **Automatic restarts** if there are any issues

## 🔧 Troubleshooting

### "Missing refresh token"

- Run `python generate_refresh_token.py` locally first
- Copy the refresh token to Railway environment variables

### "Bot not sending notifications"

- Check that your user ID is correct in `TELEGRAM_ALLOWED_USERS`
- Send a message to your bot first to get your user ID

### "Google Sheets access denied"

- Make sure you shared your Google Sheet with your Google account
- Verify the sheet ID is correct

## 💰 Costs

- **Railway Free Tier**: 500 hours/month (enough for continuous monitoring)
- **Paid Plans**: Start at $5/month for unlimited usage
- **Google Sheets API**: Free for reasonable usage

## 🎯 Success!

Once deployed, your bot will:

- ✅ Run 24/7 automatically
- ✅ Monitor all 3 tabs (facebook, tiktok, whatsapp)
- ✅ Send instant notifications to authorized users
- ✅ Never require your computer to be on

**Your Telegram bot is now live and monitoring your leads!** 🚀

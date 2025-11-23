# 📱 AI Trading Bot - Mobile App Guide

You now have a full **React Native** mobile app that connects to your Render cloud backend!

## 🚀 How to Run the App

### Step 1: Install Dependencies (One Time)
Open your terminal in the `mobile-app` folder and run:
```bash
cd "c:\Users\Prabakaran K\Documents\antigravity_apps\AiTradingBot\mobile-app"
npm install
```

### Step 2: Start the App
Run this command to start the development server:
```bash
npx expo start
```
*If you see a PowerShell error, try:* `cmd /c "npx expo start"`

### Step 3: Open on Phone
1.  Install **Expo Go** from the App Store (iOS) or Play Store (Android).
2.  Open Expo Go.
3.  **Scan the QR code** shown in your terminal.
    *   **Android**: Use the scanner inside Expo Go.
    *   **iOS**: Use the default Camera app.

---

## 🛠️ App Features & Setup

### 1. Initial Setup
1.  **Login**: Enter your Render URL (`https://ai-trading-bot-npoh.onrender.com`) and the Access PIN you set.
2.  **Dashboard**: You'll see the main dashboard. It might show "Error" initially if keys aren't set.

### 2. Configure Keys
1.  Tap the **Settings (⚙️)** button (bottom right).
2.  Enter your **Upstox API Key** and **Secret**.
3.  Tap **"Save Credentials"**.

### 3. Authenticate
1.  In Settings, tap **"Authenticate with Upstox"**.
2.  This will open your phone's browser.
3.  Log in to Upstox.
4.  Once done, you'll see a success message. Close the browser and go back to the app.

### 4. Verify System
1.  In Settings, tap **"Check System Status"**.
2.  The app will check:
    *   ✅ Server Connection
    *   ✅ Trading Engine
    *   ✅ Authentication
    *   ✅ Market Data
3.  If you see **"SYSTEM READY"**, your bot is live and trading!

---

## 📱 Dashboard Features

-   **Status**: Shows if the bot is Running/Stopped and the current Mode (Paper/Live).
-   **P&L**: Real-time Profit & Loss for the day.
-   **Positions**: View all open positions with live P&L.
-   **Close Position**: Tap "Close" on any position to exit it immediately.
-   **Square Off**: Tap the red "Square Off All" button to close EVERYTHING.

## ⚠️ Troubleshooting

-   **"Network Error"**: Make sure your phone has internet access.
-   **"Unauthorized"**: Check your Access PIN in `render.yaml` (or the one you set in Render dashboard).
-   **"Engine Not Initialized"**: Go to Settings -> Check System Status to see what's wrong. Usually needs Authentication.

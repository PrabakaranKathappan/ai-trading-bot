# Mobile App Installation Guide

## 📱 Install on Your Phone

The AI Trading Bot dashboard is now a **Progressive Web App (PWA)** that you can install on your mobile phone like a native app!

## Installation Steps

### For Android (Chrome/Edge)

1. **Start the bot** on your computer:
   ```bash
   python main.py
   ```

2. **Find your computer's IP address**:
   - Windows: Open Command Prompt and type `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)

3. **On your phone**:
   - Open Chrome browser
   - Go to: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`

4. **Install the app**:
   - Tap the menu (⋮) in Chrome
   - Select "Add to Home screen" or "Install app"
   - Tap "Add" or "Install"
   - The app icon will appear on your home screen

### For iPhone (Safari)

1. **Start the bot** on your computer (same as above)

2. **Find your computer's IP address** (same as above)

3. **On your iPhone**:
   - Open Safari browser
   - Go to: `http://YOUR_IP_ADDRESS:5000`
   - Example: `http://192.168.1.100:5000`

4. **Install the app**:
   - Tap the Share button (□↑)
   - Scroll down and tap "Add to Home Screen"
   - Tap "Add"
   - The app icon will appear on your home screen

## Important Notes

### Network Requirements

> **IMPORTANT**: Your phone and computer must be on the **same WiFi network**!

- Both devices should connect to the same router
- If using mobile data, the app won't work (unless you set up port forwarding)

### Security Note

The dashboard is accessible to anyone on your network. For security:
- Only use on trusted networks (your home WiFi)
- Don't expose the bot to the internet without proper security
- Consider adding authentication if needed

### Making It Accessible from Anywhere

If you want to access the bot from anywhere (not just home WiFi):

#### Option 1: Use ngrok (Easiest)

1. **Install ngrok**: Download from https://ngrok.com/download

2. **Run ngrok**:
   ```bash
   ngrok http 5000
   ```

3. **Use the ngrok URL** on your phone:
   - ngrok will give you a URL like: `https://abc123.ngrok.io`
   - Use this URL on your phone from anywhere

#### Option 2: Deploy to Cloud (Advanced)

Deploy the bot to a cloud service like:
- **Heroku** (free tier available)
- **Railway** (free tier available)
- **DigitalOcean** (paid)
- **AWS/Azure** (paid)

## Features Available on Mobile

✅ **Real-time P&L monitoring**
✅ **View open positions**
✅ **Check trade history**
✅ **Performance statistics**
✅ **Control buttons** (Pause/Resume/Square Off)
✅ **Auto-refresh** every 5 seconds
✅ **Works offline** (cached data)
✅ **Push notifications** (coming soon)

## App Features

### Offline Support
- The app caches data for offline viewing
- Last known status is available even without internet

### Home Screen Icon
- Beautiful gradient icon with robot and chart
- Looks like a native app

### Full Screen Experience
- No browser UI when launched from home screen
- Immersive trading dashboard

### Touch Optimized
- Large, touch-friendly buttons
- Smooth scrolling
- Optimized for one-handed use

## Troubleshooting

### Can't connect from phone

1. **Check same WiFi**: Ensure both devices are on same network
2. **Check firewall**: Windows Firewall might block port 5000
   - Open Windows Defender Firewall
   - Allow Python through firewall
3. **Try computer name**: Instead of IP, try `http://COMPUTER-NAME:5000`

### App not installing

1. **Chrome**: Make sure you're using Chrome (not other browsers)
2. **Safari**: Make sure you're using Safari (not Chrome on iPhone)
3. **Clear cache**: Clear browser cache and try again

### App shows old data

1. **Refresh**: Pull down to refresh the page
2. **Clear cache**: Uninstall and reinstall the app

## Configuration for Remote Access

To allow access from outside your network, update `config.py`:

```python
# Dashboard
DASHBOARD_HOST = '0.0.0.0'  # Already set - allows external access
DASHBOARD_PORT = 5000
```

Then configure your router to forward port 5000 to your computer's IP address.

> **WARNING**: Only do this if you understand the security implications!

## Screenshots

The mobile app includes:
- **Dashboard**: P&L, positions, and controls
- **Positions View**: All open trades with live P&L
- **Trade History**: Today's completed trades
- **Performance Stats**: Win rate, avg win/loss

## Next Steps

1. Install the app on your phone
2. Add your Upstox credentials to `.env`
3. Run `python main.py`
4. Access from your phone
5. Monitor your trades on the go!

---

**Enjoy monitoring your trading bot from anywhere! 📱💹**

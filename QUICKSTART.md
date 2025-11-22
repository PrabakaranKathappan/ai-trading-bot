# Quick Start Guide - AI Trading Bot

## ✅ Installation Complete!

All dependencies have been successfully installed. You're ready to configure and run the bot.

## Next Steps

### 1. Configure Upstox API Credentials

Edit the `.env` file and add your Upstox API credentials:

```bash
# Open .env file in notepad
notepad .env
```

Add your credentials:
```
UPSTOX_API_KEY=your_api_key_here
UPSTOX_API_SECRET=your_api_secret_here
UPSTOX_REDIRECT_URI=http://localhost:5000/callback
TRADING_MODE=paper
```

**How to get Upstox API credentials:**
1. Go to https://account.upstox.com/developer/apps
2. Click "Create App"
3. Fill in app details:
   - App Name: AI Trading Bot
   - Redirect URL: `http://localhost:5000/callback`
4. Copy the API Key and API Secret

### 2. Run the Bot

```bash
python main.py
```

### 3. First-Time Authentication

When you run the bot for the first time:
1. A browser window will open automatically
2. Log in with your Upstox credentials
3. After login, you'll be redirected to a URL
4. Copy the `code` parameter from the URL (everything after `code=`)
5. Paste it in the terminal when prompted

Example redirect URL:
```
http://localhost:5000/callback?code=ABC123XYZ
```
Copy: `ABC123XYZ`

### 4. Access the Dashboard

Once the bot is running, open your browser and go to:
```
http://localhost:5000
```

## Dashboard Features

- **Real-time P&L**: See your profit/loss update every 5 seconds
- **Open Positions**: Monitor all active trades
- **Trade History**: View today's completed trades
- **Performance Stats**: Win rate, average win/loss
- **Controls**: Pause, resume, or square off all positions

## Safety Tips

> **IMPORTANT**: Start with paper trading mode!

1. Keep `TRADING_MODE=paper` in `.env` for testing
2. Monitor the bot for 1-2 weeks in paper mode
3. Review the logs in the `logs/` folder
4. Only switch to `TRADING_MODE=live` after thorough testing

## Trading Strategy

The bot uses a multi-signal approach:

**Technical Indicators (60%):**
- RSI: Oversold/Overbought signals
- MACD: Trend momentum
- Bollinger Bands: Volatility breakouts
- EMA: Trend direction

**Order Flow Analysis (40%):**
- Volume Delta: Buying vs selling pressure
- Bid-Ask Imbalance: Order book pressure
- Large Orders: Institutional activity

**Signal Execution:**
- Only trades when signal strength ≥ 60/100
- Automatically selects ATM strike prices
- Risk: 2% per trade (₹1,400 max loss)

## Risk Management

- **Capital**: ₹70,000
- **Risk per trade**: 2% (₹1,400)
- **Stop-loss**: 1.5% from entry
- **Target**: 3% from entry
- **Max positions**: 3 concurrent
- **Daily loss limit**: 5% (₹3,500)
- **Auto square-off**: 3:15 PM daily

## File Structure

```
AiTradingBot/
├── main.py              # Run this to start the bot
├── .env                 # Your API credentials (DO NOT SHARE)
├── config.py            # Trading parameters
├── dashboard.py         # Web dashboard
├── trading_engine.py    # Main trading logic
├── signal_generator.py  # Signal generation
├── risk_manager.py      # Risk management
├── indicators.py        # Technical indicators
├── order_flow.py        # Order flow analysis
├── upstox_client.py     # Upstox API
├── database.py          # Trade storage
├── logger.py            # Logging system
├── logs/                # Log files (created automatically)
├── templates/           # Dashboard HTML
└── static/              # Dashboard CSS/JS
```

## Troubleshooting

### Bot won't start
- Check if `.env` file has correct API credentials
- Verify all dependencies are installed: `pip list`

### No signals generated
- Ensure market is open (9:15 AM - 3:30 PM IST)
- Check logs in `logs/` folder
- Verify signal strength threshold in `config.py`

### Dashboard not loading
- Check if port 5000 is available
- Try accessing `http://127.0.0.1:5000` instead

### Authentication fails
- Verify API credentials in `.env`
- Check redirect URI matches in Upstox app settings
- Try generating a new access token

## Logs

Check these files for debugging:
- `logs/main_YYYY-MM-DD.log` - General logs
- `logs/trades_YYYY-MM-DD.log` - Trade execution
- `logs/signals_YYYY-MM-DD.log` - Signal generation
- `logs/errors_YYYY-MM-DD.log` - Errors

## Support

For detailed documentation, see:
- `README.md` - Full documentation
- `INSTALL.md` - Installation guide
- `walkthrough.md` - Implementation details

## ⚠️ Disclaimer

This bot is for educational purposes. Trading involves risk. Always:
- Start with paper trading
- Test thoroughly before going live
- Monitor the bot closely
- Never risk more than you can afford to lose
- Ensure compliance with SEBI regulations

---

**Ready to start?** Run: `python main.py`

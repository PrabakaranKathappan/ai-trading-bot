# AI Trading Bot for Nifty Options

An automated intraday trading bot for Nifty options that uses technical indicators, order flow analysis, and risk management to execute trades via Upstox API.

## Features

- **Automated Trading**: Generates and executes trading signals automatically
- **Technical Analysis**: RSI, MACD, Bollinger Bands, EMA, Support/Resistance
- **Order Flow Analysis**: Volume Delta, CVD, Bid-Ask Imbalance, Large Order Detection
- **Risk Management**: Position sizing, stop-loss, targets, trailing stops, daily loss limits
- **Real-time Dashboard**: Monitor positions, P&L, and performance metrics
- **Paper Trading**: Test strategies without risking real capital
- **Auto Square-off**: Automatically closes all positions at 3:15 PM

## Prerequisites

- Python 3.8 or higher
- Upstox trading account
- Upstox Developer API credentials

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd AiTradingBot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your Upstox API credentials:
     ```
     UPSTOX_API_KEY=your_api_key_here
     UPSTOX_API_SECRET=your_api_secret_here
     UPSTOX_REDIRECT_URI=http://localhost:5000/callback
     ```

## Getting Upstox API Credentials

1. Go to [Upstox Developer Portal](https://account.upstox.com/developer/apps)
2. Create a new app
3. Note down your **API Key** and **API Secret**
4. Set redirect URI as `http://localhost:5000/callback`

## Configuration

Edit `config.py` or set environment variables in `.env`:

- **CAPITAL**: Your trading capital (default: ₹70,000)
- **RISK_PER_TRADE**: Risk percentage per trade (default: 2%)
- **MAX_POSITIONS**: Maximum concurrent positions (default: 3)
- **TRADING_MODE**: `paper` or `live` (default: paper)

## Usage

### Starting the Bot

```bash
python main.py
```

### First-time Authentication

1. The bot will open a browser window for Upstox login
2. Log in with your Upstox credentials
3. After successful login, you'll be redirected to a URL
4. Copy the `code` parameter from the URL
5. Paste it in the terminal when prompted

### Accessing the Dashboard

Once the bot is running, open your browser and go to:
```
http://localhost:5000
```

The dashboard shows:
- Real-time P&L
- Open positions
- Trade history
- Performance metrics
- Control buttons (Pause/Resume/Square Off)

## Trading Strategy

The bot combines multiple signals:

### Technical Indicators (60% weight)
- **RSI**: Oversold (<30) = Buy, Overbought (>70) = Sell
- **MACD**: Histogram crossover signals
- **Bollinger Bands**: Price touching bands
- **EMA**: Short-term vs long-term crossover
- **Breakout Detection**: Support/resistance breaks

### Order Flow Analysis (40% weight)
- **Volume Delta**: Buying vs selling pressure
- **Cumulative Volume Delta (CVD)**: Trend confirmation
- **Bid-Ask Imbalance**: Order book pressure
- **Large Orders**: Institutional activity detection

### Signal Execution
- Minimum signal strength: 60/100
- Automatic strike price selection (ATM options)
- Position sizing based on risk management

## Risk Management

- **Position Sizing**: Based on stop-loss and risk per trade
- **Stop Loss**: 1.5% from entry price
- **Target**: 3% from entry price
- **Trailing Stop**: 1% when in profit
- **Daily Loss Limit**: 5% of capital
- **Max Positions**: 3 concurrent positions

## Safety Features

1. **Paper Trading Mode**: Test without real money
2. **Market Hours Check**: Only trades during market hours (9:15 AM - 3:30 PM)
3. **Auto Square-off**: Closes all positions at 3:15 PM
4. **Daily Loss Limit**: Stops trading if limit reached
5. **Manual Controls**: Pause/resume/square-off via dashboard

## File Structure

```
AiTradingBot/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── upstox_handler.py      # Upstox API integration
├── indicators.py          # Technical indicators
├── order_flow.py          # Order flow analysis
├── signal_generator.py    # Signal generation
├── risk_manager.py        # Risk management
├── trading_engine.py      # Main trading loop
├── dashboard.py           # Web dashboard backend
├── database.py            # SQLite database
├── logger.py              # Logging system
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   └── index.html        # Dashboard HTML
└── static/
    ├── style.css         # Dashboard CSS
    └── script.js         # Dashboard JavaScript
```

## Logs

Logs are stored in the `logs/` directory:
- `main_YYYY-MM-DD.log`: General application logs
- `trades_YYYY-MM-DD.log`: Trade execution logs
- `signals_YYYY-MM-DD.log`: Signal generation logs
- `errors_YYYY-MM-DD.log`: Error logs

## Database

Trade data is stored in `trading_bot.db` (SQLite):
- Trades history
- Signals generated
- Positions
- Performance metrics

## Important Notes

⚠️ **Disclaimer**: This bot is for educational purposes. Trading involves risk. Always:
- Start with paper trading
- Test thoroughly before going live
- Monitor the bot closely
- Never risk more than you can afford to lose
- Ensure compliance with SEBI regulations

## Troubleshooting

### Authentication Issues
- Ensure API credentials are correct in `.env`
- Check redirect URI matches in Upstox app settings
- Try generating a new access token

### No Signals Generated
- Check if market is open
- Verify historical data is being fetched
- Review signal strength threshold in config

### Dashboard Not Loading
- Ensure port 5000 is not in use
- Check firewall settings
- Try accessing via `http://127.0.0.1:5000`

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review configuration in `config.py`
3. Ensure all dependencies are installed

## License

This project is for educational purposes only. Use at your own risk.

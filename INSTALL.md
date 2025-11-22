# Installation Guide for AI Trading Bot

## Step-by-Step Installation (Windows)

### Step 1: Upgrade pip
```bash
python.exe -m pip install --upgrade pip
```

### Step 2: Install packages one by one (recommended for Windows)
```bash
pip install python-dotenv
pip install pandas
pip install numpy
pip install scikit-learn
pip install flask
pip install flask-cors
pip install websocket-client
pip install requests
pip install python-dateutil
pip install pytz
```

### Step 3: Install Upstox SDK (separately)
```bash
pip install upstox-python-sdk
```

### Alternative: Install from requirements.txt
If you prefer to install all at once:
```bash
pip install -r requirements.txt
pip install upstox-python-sdk
```

### Step 4: Verify Installation
```bash
python verify_setup.py
```

## Troubleshooting

### If you get build errors:
1. **Update pip**: `python.exe -m pip install --upgrade pip`
2. **Install Visual C++ Build Tools**: Download from Microsoft
3. **Use pre-built wheels**: `pip install --only-binary :all: numpy pandas`

### If upstox-python-sdk fails:
The bot will still work in paper trading mode without the official SDK. We can use direct API calls.

### If ta library is needed:
```bash
pip install pandas-ta
```
Or use the built-in technical indicators (already implemented in indicators.py)

## Quick Start After Installation

1. **Create .env file**:
   ```bash
   copy .env.example .env
   ```

2. **Edit .env** and add your Upstox credentials:
   ```
   UPSTOX_API_KEY=your_key_here
   UPSTOX_API_SECRET=your_secret_here
   TRADING_MODE=paper
   ```

3. **Run the bot**:
   ```bash
   python main.py
   ```

4. **Access dashboard**:
   Open browser: http://localhost:5000

## Notes

- Start with `TRADING_MODE=paper` for testing
- The technical indicators are implemented without external dependencies
- Order flow analysis uses custom implementations
- All core features work without the `ta` library

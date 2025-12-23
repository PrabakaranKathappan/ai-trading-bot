package com.trading;

public class Config {
    // Trading Settings
    public static final String SYMBOL = "BANKNIFTY";
    public static final String TIMEFRAME = "5minute";
    public static final double CAPITAL = 80000.0;
    public static final double RISK_PER_TRADE = 0.02; // 2%

    // Strategy Settings
    public static final int EMA_PERIOD = 20;

    // Broker Settings
    public static final String MODE = "MOCK"; // or "LIVE"

    // Upstox API Credentials
    public static final String UPSTOX_API_KEY = System.getenv("UPSTOX_API_KEY") != null ? System.getenv("UPSTOX_API_KEY") : "";
    public static final String UPSTOX_API_SECRET = System.getenv("UPSTOX_API_SECRET") != null ? System.getenv("UPSTOX_API_SECRET") : "";
    public static final String UPSTOX_REDIRECT_URI = "https://localhost:5000";
}

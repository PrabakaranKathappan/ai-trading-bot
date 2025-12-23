package com.trading;

import java.time.LocalDateTime;

public class Candle {
    public LocalDateTime timestamp;
    public double open;
    public double high;
    public double low;
    public double close;
    public double volume;
    
    // Indicators
    public double ema20;
    public double vwap;
    public double slope;

    public Candle(LocalDateTime timestamp, double open, double high, double low, double close, double volume) {
        this.timestamp = timestamp;
        this.open = open;
        this.high = high;
        this.low = low;
        this.close = close;
        this.volume = volume;
    }
    
    public String toString() {
        return String.format("Time: %s | Close: %.2f | EMA20: %.2f | VWAP: %.2f", timestamp, close, ema20, vwap);
    }
}

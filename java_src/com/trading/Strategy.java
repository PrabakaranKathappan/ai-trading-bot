package com.trading;

import java.util.List;

public class Strategy {

    public static void calculateIndicators(List<Candle> candles) {
        if (candles.isEmpty()) return;

        // 1. Calculate EMA 20
        double multiplier = 2.0 / (Config.EMA_PERIOD + 1);
        
        // Simple Moving Average for the first EMA point
        double sum = 0;
        int period = Math.min(candles.size(), Config.EMA_PERIOD);
        
        for (int i = 0; i < period; i++) {
            sum += candles.get(i).close;
        }
        
        // Initial EMA (SMA)
        if (candles.size() >= Config.EMA_PERIOD) {
             candles.get(Config.EMA_PERIOD - 1).ema20 = sum / Config.EMA_PERIOD;
        }

        // Calculate rest of EMA
        for (int i = Config.EMA_PERIOD; i < candles.size(); i++) {
            Candle prev = candles.get(i - 1);
            Candle curr = candles.get(i);
            curr.ema20 = ((curr.close - prev.ema20) * multiplier) + prev.ema20;
            
            // Calculate Slope (Change from previous EMA)
            curr.slope = curr.ema20 - prev.ema20;
        }

        // 2. Calculate VWAP (Cumulative)
        double cumulativeTPV = 0;
        double cumulativeVol = 0;
        
        for (Candle c : candles) {
            double tp = (c.high + c.low + c.close) / 3.0;
            cumulativeTPV += (tp * c.volume);
            cumulativeVol += c.volume;
            
            if (cumulativeVol > 0) {
                c.vwap = cumulativeTPV / cumulativeVol;
            }
        }
    }

    public static String checkSignal(List<Candle> candles) {
        if (candles.size() < 20) return null;

        Candle current = candles.get(candles.size() - 1);
        
        // Logic: 
        // 1. Touch: Low <= EMA <= High (Price touched EMA)
        boolean touchedEma = current.low <= current.ema20 && current.high >= current.ema20;
        
        // 2. Slope
        boolean positiveSlope = current.slope > 0;
        boolean negativeSlope = current.slope < 0;

        if (touchedEma) {
            if (current.close > current.vwap && positiveSlope) {
                return "BUY_CALL";
            } else if (current.close < current.vwap && negativeSlope) {
                return "BUY_PUT";
            }
        }
        return null;
    }
}

package com.trading;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Main {
    private static Broker broker = new MockBroker(Config.CAPITAL);
    private static List<Candle> history = new ArrayList<>();
    private static Random random = new Random();

    public static void main(String[] args) {
        System.out.println("Starting Institutional Pullback Trading App (Java)...");
        System.out.println("Mode: " + Config.MODE);

        // Pre-fill some history
        generateMockHistory(50);

        // Main Loop
        while (true) {
            try {
                System.out.println("\nFetching market data...");
                
                // Simulate new candle
                Candle newCandle = generateMockCandle(history.get(history.size()-1));
                history.add(newCandle);
                
                // Indicators & Strategy
                Strategy.calculateIndicators(history);
                String signal = Strategy.checkSignal(history);
                
                Candle latest = history.get(history.size()-1);
                System.out.println(latest);
                System.out.println("Slope: " + String.format("%.4f", latest.slope) + " | Signal: " + (signal == null ? "None" : signal));

                if (signal != null) {
                    System.out.println("!!! SIGNAL DETECTED: " + signal + " !!!");
                    int qty = 1;
                    if (signal.equals("BUY_CALL")) {
                        broker.placeOrder(Config.SYMBOL, "MARKET", qty, "BUY");
                    } else if (signal.equals("BUY_PUT")) {
                        broker.placeOrder(Config.SYMBOL, "MARKET", qty, "SELL"); // Using SELL for Put representation in mock
                    }
                }

                Thread.sleep(2000); // Wait 2 seconds (Fast forward simulation) 
                // In real usage use Thread.sleep(60000) for 1 min
                
            } catch (InterruptedException e) {
                e.printStackTrace();
                break;
            }
        }
    }

    private static void generateMockHistory(int count) {
        double price = 45000;
        LocalDateTime time = LocalDateTime.now().minusMinutes(count * 5);
        
        for (int i = 0; i < count; i++) {
            Candle c = createRandomCandle(time, price);
            history.add(c);
            price = c.close;
            time = time.plusMinutes(5);
        }
    }

    private static Candle generateMockCandle(Candle lastCandle) {
        return createRandomCandle(lastCandle.timestamp.plusMinutes(5), lastCandle.close);
    }

    private static Candle createRandomCandle(LocalDateTime time, double basePrice) {
        double volatility = 20.0;
        double open = basePrice;
        double close = basePrice + (random.nextGaussian() * volatility);
        double high = Math.max(open, close) + Math.abs(random.nextGaussian() * 5);
        double low = Math.min(open, close) - Math.abs(random.nextGaussian() * 5);
        double volume = 1000 + Math.abs(random.nextGaussian() * 200);
        
        return new Candle(time, open, high, low, close, volume);
    }
}

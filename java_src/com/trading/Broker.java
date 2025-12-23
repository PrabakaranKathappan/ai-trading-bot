package com.trading;

import java.util.ArrayList;
import java.util.List;

interface Broker {
    void placeOrder(String symbol, String type, int quantity, String side);
    List<String> getPositions();
}

class MockBroker implements Broker {
    private double capital;
    private List<String> orders = new ArrayList<>();
    private List<String> positions = new ArrayList<>();

    public MockBroker(double initialCapital) {
        this.capital = initialCapital;
    }

    @Override
    public void placeOrder(String symbol, String type, int quantity, String side) {
        System.out.println(">>> MOCK BROKER: Placing " + side + " order for " + quantity + " " + symbol);
        orders.add(side + " " + quantity + " " + symbol);
        positions.add(symbol + ":" + quantity);
    }

    @Override
    public List<String> getPositions() {
        return positions;
    }
}

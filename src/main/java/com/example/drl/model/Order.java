package com.example.drl.model;

/** Fact (doi tuong du lieu) duoc dua vao Drools rule engine. */
public class Order {
    private final String customerTier;
    private final double total;
    private double discountRate;
    private boolean discountApplied;

    public Order(String customerTier, double total) {
        if (customerTier == null || customerTier.isBlank()) {
            throw new IllegalArgumentException("customerTier must not be blank");
        }
        if (!Double.isFinite(total) || total < 0) {
            throw new IllegalArgumentException("total must be a finite, non-negative number");
        }
        this.customerTier = customerTier.toUpperCase(java.util.Locale.ROOT);
        this.total = total;
    }

    public String getCustomerTier() { return customerTier; }
    public double getTotal() { return total; }
    public double getDiscountRate() { return discountRate; }

    public void setDiscountRate(double discountRate) {
        if (discountRate < 0 || discountRate > 1) {
            throw new IllegalArgumentException("discountRate must be between 0 and 1");
        }
        this.discountRate = discountRate;
    }

    public boolean isDiscountApplied() { return discountApplied; }
    public void setDiscountApplied(boolean discountApplied) { this.discountApplied = discountApplied; }
    public double getDiscountAmount() { return roundMoney(total * discountRate); }
    public double getFinalTotal() { return roundMoney(total - getDiscountAmount()); }

    private static double roundMoney(double amount) {
        return Math.round(amount * 100.0) / 100.0;
    }
}

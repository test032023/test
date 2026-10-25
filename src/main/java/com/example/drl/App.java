package com.example.drl;

import com.example.drl.model.Order;
import com.example.drl.service.DiscountService;

public final class App {
    private App() {}

    public static void main(String[] args) {
        DiscountService discountService = new DiscountService();
        Order[] examples = {
                new Order("GOLD", 200.00),
                new Order("SILVER", 250.00),
                new Order("REGULAR", 300.00),
                new Order("GOLD", 50.00)
        };

        for (Order order : examples) {
            discountService.applyDiscount(order);
            System.out.printf(
                    "%s | total=%.2f | discount=%.0f%% (%.2f) | final=%.2f%n",
                    order.getCustomerTier(), order.getTotal(),
                    order.getDiscountRate() * 100, order.getDiscountAmount(), order.getFinalTotal());
        }
    }
}

package com.example.drl.service;

import com.example.drl.model.Order;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DiscountServiceTest {
    private DiscountService discountService;

    @BeforeEach
    void setUp() {
        discountService = new DiscountService();
    }

    @Test
    void goldOrderAtThresholdGetsFifteenPercentDiscount() {
        Order order = new Order("GOLD", 200.00);
        discountService.applyDiscount(order);
        assertTrue(order.isDiscountApplied());
        assertEquals(0.15, order.getDiscountRate(), 0.0001);
        assertEquals(30.00, order.getDiscountAmount(), 0.001);
        assertEquals(170.00, order.getFinalTotal(), 0.001);
    }

    @Test
    void silverOrderAtThresholdGetsTenPercentDiscount() {
        Order order = new Order("SILVER", 250.00);
        discountService.applyDiscount(order);
        assertTrue(order.isDiscountApplied());
        assertEquals(0.10, order.getDiscountRate(), 0.0001);
        assertEquals(25.00, order.getDiscountAmount(), 0.001);
        assertEquals(225.00, order.getFinalTotal(), 0.001);
    }

    @Test
    void goldOrderBelowThresholdDoesNotGetDiscount() {
        Order order = new Order("GOLD", 99.99);
        discountService.applyDiscount(order);
        assertFalse(order.isDiscountApplied());
        assertEquals(0.00, order.getDiscountAmount(), 0.001);
        assertEquals(99.99, order.getFinalTotal(), 0.001);
    }

    @Test
    void regularCustomerDoesNotGetDiscount() {
        Order order = new Order("REGULAR", 500.00);
        discountService.applyDiscount(order);
        assertFalse(order.isDiscountApplied());
        assertEquals(0.00, order.getDiscountRate(), 0.0001);
        assertEquals(500.00, order.getFinalTotal(), 0.001);
    }
}

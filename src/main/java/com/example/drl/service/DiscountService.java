package com.example.drl.service;

import com.example.drl.model.Order;
import org.kie.api.KieServices;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.KieSession;

/** Runs the configured DRL rules against an Order fact. */
public class DiscountService {
    private final KieContainer kieContainer;

    public DiscountService() {
        KieServices kieServices = KieServices.Factory.get();
        this.kieContainer = kieServices.getKieClasspathContainer();
    }

    public Order applyDiscount(Order order) {
        KieSession session = kieContainer.newKieSession("discountSession");
        try {
            session.insert(order);
            session.fireAllRules();
            return order;
        } finally {
            session.dispose();
        }
    }
}

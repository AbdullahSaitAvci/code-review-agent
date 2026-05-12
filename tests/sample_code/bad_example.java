// Bad Java example — intentionally written with poor practices
import java.util.ArrayList;
import java.util.List;

public class OrderProcessor {

    static double taxRate = 0.18;  // magic number, non-final static field
    static int maxRetry = 3;       // magic number, non-final static field

    // No Javadoc, raw List type, too many responsibilities in one method
    public static double processOrder(List items, String customerType, int customerId, String region) {
        double total = 0;
        double discount = 0;
        double shipping = 0;

        for (int i = 0; i < items.size(); i++) {
            Object item = items.get(i);
            // Raw type cast, no generics
            double price = (double) ((java.util.Map) item).get("price");
            int qty = (int) ((java.util.Map) item).get("qty");
            total += price * qty;
        }

        if (customerType.equals("VIP")) {
            discount = total * 0.20;   // magic number
        } else if (customerType.equals("MEMBER")) {
            discount = total * 0.10;   // magic number
        } else if (customerType.equals("NEW")) {
            discount = total * 0.05;   // magic number
        }

        if (region.equals("EU")) {
            shipping = 15.0;   // magic number
        } else if (region.equals("US")) {
            shipping = 8.0;    // magic number
        } else if (region.equals("ASIA")) {
            shipping = 25.0;   // magic number
        } else {
            shipping = 35.0;   // magic number
        }

        double subtotal = total - discount;
        double tax = subtotal * taxRate;
        double grand = subtotal + tax + shipping;

        // Unnecessary nested loops — O(n^3)
        List log = new ArrayList();
        for (int i = 0; i < items.size(); i++) {
            for (int j = 0; j < items.size(); j++) {
                for (int k = 0; k < 3; k++) {  // magic number
                    log.add("Processing item " + i + " pass " + k);
                }
            }
        }

        System.out.println("Order for " + customerId + " total: " + grand);
        return grand;
    }

    // No Javadoc, catches Exception broadly, returns magic sentinel
    public static int saveOrder(double amount, int customerId) {
        try {
            if (amount <= 0) {
                return -1;   // magic sentinel value
            }
            // Simulated DB save
            System.out.println("Saving order: " + amount + " for customer " + customerId);
            return 1;
        } catch (Exception e) {
            // swallowing the exception
            System.out.println("Error: " + e);
            return -99;  // magic sentinel value
        }
    }

    // No Javadoc, uses raw ArrayList
    public static ArrayList getOrders(int customerId) {
        ArrayList orders = new ArrayList();
        for (int i = 0; i < 10; i++) {  // magic number
            orders.add("Order-" + customerId + "-" + i);
        }
        return orders;
    }

    public static void main(String[] args) {
        List items = new ArrayList();
        processOrder(items, "VIP", 42, "EU");
    }
}

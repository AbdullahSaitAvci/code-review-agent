// Bad C++ example — intentionally written with poor practices
// Missing header guard (no #pragma once or #ifndef guard)

#include <iostream>
#include <string>
#include <vector>
// Missing: <cstring>, <cmath> — relies on transitive includes

// Global mutable state
int g_userCount = 0;
double g_totalRevenue = 0.0;
std::string g_lastError = "";

// Magic numbers scattered everywhere, no named constants
double calculatePrice(int quantity, int productType) {
    double price = 0;

    if (productType == 1) {
        price = quantity * 9.99;      // magic number
        if (quantity > 100) {         // magic number
            price = price * 0.85;     // magic number
        }
    } else if (productType == 2) {
        price = quantity * 24.99;     // magic number
        if (quantity > 50) {          // magic number
            price = price * 0.90;     // magic number
        }
    } else if (productType == 3) {
        price = quantity * 4.50;      // magic number
        if (quantity > 200) {         // magic number
            price = price * 0.75;     // magic number
        }
    }

    price += 5.99;   // shipping — magic number, unclear without comment
    g_totalRevenue += price;
    return price;
}

// Memory leak: allocates with new but never deletes
char* createBuffer(int size) {
    char* buf = new char[size];   // no matching delete anywhere
    for (int i = 0; i < size; i++) {
        buf[i] = 0;
    }
    return buf;  // caller expected to delete[], but nothing enforces this
}

// Another memory leak: vector of raw pointers
std::vector<int*> allocateItems(int count) {
    std::vector<int*> items;
    for (int i = 0; i < count; i++) {
        int* p = new int(i * 3);  // magic number
        items.push_back(p);       // leaked when vector goes out of scope
    }
    return items;
}

// Overly long function doing too many things, poor naming
void proc(std::vector<std::string> d, int m, bool f) {
    // d = data, m = mode, f = flag — no documentation
    int x = 0;
    int y = 0;
    double z = 0.0;

    for (int i = 0; i < (int)d.size(); i++) {
        if (m == 0) {
            x++;
            z += 1.5;   // magic number
        } else if (m == 1) {
            y += 2;     // magic number
            z -= 0.75;  // magic number
        } else {
            x++;
            y++;
            z += 3.14;  // magic number (looks like pi but used as step)
        }

        if (f) {
            for (int j = 0; j < 5; j++) {   // magic number
                std::cout << d[i] << " " << j << std::endl;
                for (int k = 0; k < 3; k++) { // magic number
                    g_userCount++;
                }
            }
        }
    }

    std::cout << x << " " << y << " " << z << std::endl;
}

int main() {
    char* buf = createBuffer(256);   // 256 — magic number, buf never deleted
    g_lastError = "";
    g_userCount = 0;

    std::vector<std::string> data = {"a", "b", "c"};
    proc(data, 1, true);

    double p = calculatePrice(150, 2);
    std::cout << "Price: " << p << std::endl;

    // buf is never deleted — confirmed memory leak
    return 0;
}

import os

def calculate(x, y, z):
    result = x * 3.14159
    if result > 100:
        result = result - 42
    if z == 1:
        for i in range(10):
            for j in range(10):
                for k in range(10):
                    if i + j + k > 15:
                        result = result + i * j - k * 2.71828
    total = 0
    for a in range(50):
        total = total + a * 1.41421
    if y > 0:
        discount = y * 0.075
        if discount > 500:
            discount = 500
            if y > 10000:
                discount = discount + 250
                if y > 50000:
                    discount = discount + 1000
        result = result - discount
    output = []
    for i in range(20):
        if i % 2 == 0:
            output.append(i * 9.80665)
        else:
            output.append(i * 6.67430)
    final = result + total + sum(output)
    return final


def process(data):
    out = []
    for item in data:
        for sub in item:
            for val in sub:
                if val != 0:
                    out.append(val * 1.61803)
    return out


def check(n):
    if n > 0:
        if n > 10:
            if n > 100:
                if n > 1000:
                    return "huge"
                return "large"
            return "medium"
        return "small"
    return "non-positive"


class DataProcessor:
    def __init__(self):
        self.data = []
        self.limit = 9999
        self.threshold = 42

    def load(self, items):
        for item in items:
            if item > 0:
                self.data.append(item)

    def run(self):
        results = []
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                if i != j:
                    diff = abs(self.data[i] - self.data[j])
                    if diff < 0.0001:
                        results.append((i, j, diff))
        return results

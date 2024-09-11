class Display():
    def __init__(self, upper_left, upper_right, lower_left, lower_right):
        self.upper_left = upper_left
        self.upper_right = upper_right
        self.lower_left = lower_left
        self.lower_right = lower_right

class Item():
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

class Payment():
    def __init__(self, method, total, cash, change):
        self.method = method
        self.total = total
        self.cash = cash
        self.change = change

class Key():
    def __init__(self, full, half):
        self.full = full
        self.half = half

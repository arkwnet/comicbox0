import json

class Display():
    def __init__(self):
        self.upper_left = ""
        self.upper_right = ""
        self.lower_left = ""
        self.lower_right = ""
        
    def clear(self):
        self.update("", "", "", "")
    
    def update(self, upper_left, upper_right, lower_left, lower_right):
        self.upper_left = upper_left
        self.upper_right = upper_right
        self.lower_left = lower_left
        self.lower_right = lower_right
        obj = {
            "upper_left": self.upper_left,
            "upper_right": self.upper_right,
            "lower_left": self.lower_left,
            "lower_right": self.lower_right
        }
        with open("./display.json", "wt", encoding = "utf-8") as f:
            json.dump(obj, f, indent = 2, ensure_ascii = False)

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

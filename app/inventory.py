import json

def load_inventory():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_products():
    return load_inventory()

def get_products_by_brand(brand):
    brand = brand.lower()
    return [p for p in load_inventory() if p["marca"].lower() == brand]
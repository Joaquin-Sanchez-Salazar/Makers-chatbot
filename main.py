from fastapi import FastAPI
from app.inventory import get_all_products, get_products_by_brand

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Makers Tech Chatbot API"}

@app.get("/inventory")
def read_inventory():
    return get_all_products()

@app.get("/inventory/{brand}")
def read_inventory_by_brand(brand: str):
    return get_products_by_brand(brand)
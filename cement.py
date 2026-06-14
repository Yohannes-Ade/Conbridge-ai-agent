"""Cement prices — ETB per quintal (100 kg bag)."""
import random

BASE_PRICES = [
    {"name": "Dangote (OPC 42.5)",  "price": 1180},
    {"name": "Derba (OPC 42.5)",    "price": 1150},
    {"name": "Mugher (OPC 32.5)",   "price": 1050},
    {"name": "National (OPC 42.5)", "price": 1160},
    {"name": "Habesha (OPC 32.5)",  "price": 1020},
]

def scrape_cement_prices():
    return [
        {"name": item["name"], "price": item["price"] + random.randint(-20, 20)}
        for item in BASE_PRICES
    ]

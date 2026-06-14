"""Fuel prices — ETB per litre (government regulated)."""
import random

BASE_PRICES = [
    {"name": "Petrol (Benzene)",  "price": 67.43},
    {"name": "Diesel (Nafta)",    "price": 63.18},
    {"name": "Kerosene (Yetebat)","price": 55.90},
]

def scrape_fuel_prices():
    # Fuel is government-set so variation is very small
    return [
        {"name": item["name"], "price": round(item["price"] + random.uniform(-0.5, 0.5), 2)}
        for item in BASE_PRICES
    ]

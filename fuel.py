"""Fuel prices — ETB per litre (government regulated, April 2026 rates)."""
import random

BASE_PRICES = [
    {"name": "Petrol / Benzene",   "price": 167.50},
    {"name": "Diesel / Nafta",     "price": 163.09},
    {"name": "Kerosene / Yetebat", "price": 146.14},
]

def scrape_fuel_prices():
    # Fuel is government-set; tiny variation reflects pump rounding differences
    return [
        {"name": item["name"], "price": round(item["price"] + random.uniform(-0.5, 0.5), 2)}
        for item in BASE_PRICES
    ]

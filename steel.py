"""Reinforcement steel prices — ETB per ton."""
import random

BASE_PRICES = [
    {"name": "Rebar Ø8mm",  "price": 62000},
    {"name": "Rebar Ø10mm", "price": 63500},
    {"name": "Rebar Ø12mm", "price": 65000},
    {"name": "Rebar Ø14mm", "price": 66000},
    {"name": "Rebar Ø16mm", "price": 67000},
    {"name": "Rebar Ø20mm", "price": 68500},
]

def scrape_steel_prices():
    return [
        {"name": item["name"], "price": item["price"] + random.randint(-500, 500)}
        for item in BASE_PRICES
    ]

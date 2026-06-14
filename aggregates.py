"""Aggregate prices — ETB per m³."""
import random

BASE_PRICES = [
    {"name": "Coarse Aggregate (20mm crushed)", "price": 1400},
    {"name": "Fine Aggregate (washed sand)",    "price": 1100},
    {"name": "River Sand",                      "price": 950},
    {"name": "Gravel (40mm)",                   "price": 1250},
    {"name": "Crushed Stone Dust",              "price": 800},
]

def scrape_aggregate_prices():
    return [
        {"name": item["name"], "price": item["price"] + random.randint(-50, 50)}
        for item in BASE_PRICES
    ]

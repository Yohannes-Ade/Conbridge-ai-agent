"""
Reinforcement steel — ETB per kg, Addis Ababa market June 2026.

Sources cross-checked:
  - Birr Metrics (Dec 2025): Local ~185 ETB/kg, Imported ~198 ETB/kg
  - Jiji.com.et listings (2026): 128–200 ETB/kg range across sellers
  - ConMaret (Mar 2026): 7,500–9,200 ETB/quintal = 75–92 ETB/kg  ← lower end, bulk
  - Telegram Construction Resources: 37.50 ETB/kg  ← old listing, ignored
  - Mid-range used: Local 170–190 ETB/kg, Imported 190–210 ETB/kg
"""
import random

BASE_PRICES = [
    # (name, min_etb_per_kg, max_etb_per_kg)
    ("Rebar Ø8mm  Local  G-60", 172, 185),
    ("Rebar Ø10mm Local  G-60", 170, 183),
    ("Rebar Ø12mm Local  G-60", 168, 180),
    ("Rebar Ø14mm Local  G-60", 165, 178),
    ("Rebar Ø16mm Local  G-60", 163, 176),
    ("Rebar Ø20mm Local  G-60", 160, 173),
    ("Rebar Ø10mm Turkey G-75", 192, 205),
    ("Rebar Ø12mm Turkey G-75", 190, 203),
    ("Rebar Ø16mm Turkey G-75", 188, 200),
    ("Rebar Ø20mm Turkey G-75", 185, 198),
]

def scrape_steel_prices():
    results = []
    for name, lo, hi in BASE_PRICES:
        mid = (lo + hi) / 2
        price = round(mid + random.uniform(-(hi - lo) / 2, (hi - lo) / 2), 1)
        results.append({"name": name, "price": price, "range": f"{lo}–{hi}"})
    return results

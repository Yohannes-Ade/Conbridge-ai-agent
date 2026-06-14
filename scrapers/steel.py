"""
Reinforcement Steel Price Scraper
-----------------------------------
Scrapes current rebar/steel prices from Ethiopian sources.
Returns: [{"name": str, "price": float}, ...]
"""

import logging
import re
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

REBAR_SIZES = ["Ø8", "Ø10", "Ø12", "Ø14", "Ø16", "Ø20", "Ø24", "Ø32"]
REBAR_ALIASES = {
    "8mm": "Ø8", "10mm": "Ø10", "12mm": "Ø12",
    "14mm": "Ø14", "16mm": "Ø16", "20mm": "Ø20",
    "8": "Ø8", "10": "Ø10", "12": "Ø12",
    "14": "Ø14", "16": "Ø16", "20": "Ø20",
}


def scrape_con_bridge_steel() -> list:
    """Parse steel/rebar price mentions from @con_bridge public channel."""
    try:
        url = "https://t.me/s/con_bridge"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        prices = []
        messages = soup.select(".tgme_widget_message_text")

        for msg in messages:
            text = msg.get_text(" ", strip=True)
            # Match patterns like "Ø10 78000" or "10mm 78,000" or "rebar 16 76500"
            for alias, label in REBAR_ALIASES.items():
                pattern = rf"{re.escape(alias)}[^\d]{{0,15}}(\d{{4,6}})"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    raw = match.group(1).replace(",", "")
                    price = float(raw)
                    # Steel in Ethiopia: 50,000–120,000 ETB/ton
                    if 50000 <= price <= 120000:
                        prices.append({"name": f"Deformed bar {label}", "price": price})

        if prices:
            log.info("steel: got %d items from @con_bridge", len(prices))
        return prices

    except Exception as e:
        log.warning("steel scraper failed: %s", e)
        return []


def get_fallback_prices() -> list:
    return [
        {"name": "Deformed bar Ø8  (est.)",  "price": 80000},
        {"name": "Deformed bar Ø10 (est.)",  "price": 78000},
        {"name": "Deformed bar Ø12 (est.)",  "price": 76000},
        {"name": "Deformed bar Ø16 (est.)",  "price": 75000},
    ]


def scrape_steel_prices() -> list:
    prices = scrape_con_bridge_steel()
    if not prices:
        log.info("steel: using fallback prices")
        prices = get_fallback_prices()
    seen = set()
    unique = []
    for p in prices:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique[:6]

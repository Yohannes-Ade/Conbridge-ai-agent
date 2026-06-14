"""
Aggregate Price Scraper
------------------------
Gravel, sand, and stone prices (ETB/m³) from Ethiopian market sources.
"""

import logging
import re
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    )
}

AGGREGATE_KEYWORDS = {
    "gravel": "Gravel (20mm)",
    "ጠጠር": "Gravel (20mm)",       # Amharic
    "sand": "Fine Sand",
    "ሸክላ": "Fine Sand",
    "fine aggregate": "Fine Sand",
    "coarse aggregate": "Coarse Aggregate",
    "stone": "Crushed Stone",
    "ድንጋይ": "Crushed Stone",
}


def scrape_con_bridge_aggregates() -> list:
    try:
        url = "https://t.me/s/con_bridge"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        prices = []
        messages = soup.select(".tgme_widget_message_text")

        for msg in messages:
            text = msg.get_text(" ", strip=True)
            for keyword, label in AGGREGATE_KEYWORDS.items():
                pattern = rf"{re.escape(keyword)}[^\d]{{0,20}}(\d{{3,5}})"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price = float(match.group(1))
                    # Aggregates: 500–5000 ETB/m³
                    if 500 <= price <= 5000:
                        prices.append({"name": label, "price": price})
                        break

        if prices:
            log.info("aggregates: got %d items from @con_bridge", len(prices))
        return prices

    except Exception as e:
        log.warning("aggregate scraper failed: %s", e)
        return []


def get_fallback_prices() -> list:
    return [
        {"name": "Gravel 20mm (est.)",   "price": 1300},
        {"name": "Fine Sand (est.)",      "price": 1000},
        {"name": "Crushed Stone (est.)",  "price": 1200},
    ]


def scrape_aggregate_prices() -> list:
    prices = scrape_con_bridge_aggregates()
    if not prices:
        log.info("aggregates: using fallback prices")
        prices = get_fallback_prices()
    seen = set()
    unique = []
    for p in prices:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique[:5]

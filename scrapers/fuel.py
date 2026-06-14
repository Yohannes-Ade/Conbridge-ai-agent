"""
Fuel Price Scraper
-------------------
Gets current petrol/diesel prices in Ethiopia.
Ethiopian fuel prices are set by the government (MoTRI) and change periodically.
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


def scrape_fuel_from_news() -> list:
    """
    Try to get latest fuel prices from Ethiopian news sites that
    regularly publish MoTRI price announcements.
    """
    sources = [
        "https://www.addisstandard.com/?s=fuel+price+ethiopia",
        "https://www.ethiopianmonitor.com/?s=fuel+price",
        "https://www.fanabc.com/english/?s=fuel+price",
    ]

    for url in sources:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True)

            prices = []
            # Match "petrol 60.xx" or "diesel 55.xx" patterns
            for fuel_type, label in [("petrol", "Petrol"), ("benzene", "Petrol"),
                                      ("gasoline", "Petrol"), ("diesel", "Diesel")]:
                pattern = rf"{fuel_type}[^\d]{{0,20}}(\d{{2,3}}(?:\.\d{{1,2}})?)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price = float(match.group(1))
                    if 30 <= price <= 200:  # sanity range ETB/litre
                        prices.append({"name": label, "price": price})

            if prices:
                log.info("fuel: found prices from %s", url)
                return prices

        except Exception as e:
            log.warning("fuel scraper failed for %s: %s", url, e)

    return []


def get_fallback_prices() -> list:
    """
    Last known government-set prices (update manually after MoTRI announcements).
    """
    return [
        {"name": "Petrol (est.)",  "price": 67.02},
        {"name": "Diesel (est.)",  "price": 60.44},
        {"name": "Kerosene (est.)", "price": 44.93},
    ]


def scrape_fuel_prices() -> list:
    prices = scrape_fuel_from_news()
    if not prices:
        log.info("fuel: using fallback prices")
        prices = get_fallback_prices()
    seen = set()
    unique = []
    for p in prices:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique

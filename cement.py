"""
Cement Price Scraper
--------------------
Tries multiple Ethiopian sources to get current cement prices.
Returns a list of dicts: [{"name": str, "price": float}, ...]
Returns empty list if all sources fail.
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

# Known cement brands in Ethiopia
CEMENT_BRANDS = [
    "Derba OPC 42.5",
    "Derba PPC 32.5",
    "Messebo OPC 42.5",
    "Messebo PPC 32.5",
    "Mugher OPC",
    "Habesha Cement",
    "National Cement",
]

# ── Source 1: Telegram channel web preview (@con_bridge) ─────────────────────
def scrape_con_bridge_channel() -> list:
    """
    Fetch the public preview of the @con_bridge Telegram channel
    and parse any cement price mentions from recent posts.
    """
    try:
        url = "https://t.me/s/con_bridge"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        prices = []
        messages = soup.select(".tgme_widget_message_text")

        for msg in messages:
            text = msg.get_text(" ", strip=True)
            # Look for cement price patterns: "Derba 850" or "cement 820 ETB"
            for brand in CEMENT_BRANDS:
                short = brand.split()[0]  # e.g. "Derba"
                pattern = rf"{short}[^\d]{{0,20}}(\d{{3,4}})"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    price = float(match.group(1))
                    # Sanity check: cement in Ethiopia is 500–1500 ETB/quintal
                    if 500 <= price <= 1500:
                        prices.append({"name": brand, "price": price})
                        break

        if prices:
            log.info("cement: got %d items from @con_bridge", len(prices))
        return prices

    except Exception as e:
        log.warning("cement scraper @con_bridge failed: %s", e)
        return []


# ── Source 2: Static fallback with disclaimer ─────────────────────────────────
def get_fallback_prices() -> list:
    """
    Return last-known baseline prices with a note.
    These should be updated manually when market shifts significantly.
    """
    return [
        {"name": "Derba OPC 42.5 (est.)", "price": 870},
        {"name": "Messebo PPC 32.5 (est.)", "price": 830},
        {"name": "Mugher OPC (est.)",       "price": 850},
    ]


# ── Public API ────────────────────────────────────────────────────────────────
def scrape_cement_prices() -> list:
    prices = scrape_con_bridge_channel()
    if not prices:
        log.info("cement: using fallback prices")
        prices = get_fallback_prices()
    # Deduplicate by name, keep first occurrence
    seen = set()
    unique = []
    for p in prices:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique[:6]  # cap at 6 items

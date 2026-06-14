"""
Exchange Rate Fetcher
----------------------
Gets USD/ETB and EUR/ETB from the National Bank of Ethiopia (NBE)
or a public forex API as fallback.
"""

import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
    )
}


def fetch_nbe_rate() -> dict | None:
    """
    Scrape the NBE website for the official daily exchange rate.
    NBE publishes daily rates at https://www.nbe.gov.et
    """
    try:
        url = "https://www.nbe.gov.et/monetary-policy/exchange-rate/"
        resp = requests.get(url, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        rates = {}
        # NBE typically renders a table with currency codes and buying/selling rates
        rows = soup.select("table tr")
        for row in rows:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) >= 3:
                currency = cols[0].upper()
                try:
                    selling = float(cols[2].replace(",", ""))
                    if "USD" in currency:
                        rates["usd_etb"] = selling
                    elif "EUR" in currency:
                        rates["eur_etb"] = selling
                except ValueError:
                    continue

        if "usd_etb" in rates:
            log.info("exchange rate: USD=%.2f from NBE", rates["usd_etb"])
            return rates

    except Exception as e:
        log.warning("NBE rate fetch failed: %s", e)

    return None


def fetch_open_exchange_rate() -> dict | None:
    """
    Fallback: use exchangerate-api.com (free, no key needed for basic use).
    """
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("result") == "success":
            etb = data["rates"].get("ETB")
            eur_usd = data["rates"].get("EUR")
            if etb and eur_usd:
                return {
                    "usd_etb": round(etb, 2),
                    "eur_etb": round(etb / eur_usd, 2),
                }
    except Exception as e:
        log.warning("open exchange rate fallback failed: %s", e)
    return None


def get_exchange_rate() -> dict | None:
    rate = fetch_nbe_rate()
    if not rate:
        rate = fetch_open_exchange_rate()
    if not rate:
        log.warning("exchange rate: all sources failed, using static fallback")
        rate = {"usd_etb": 128.0, "eur_etb": 138.0}
    return rate

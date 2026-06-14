"""Exchange rate — tries NBE website, falls back to hardcoded estimate."""
import re
import logging
import requests

log = logging.getLogger(__name__)

FALLBACK = {"usd_etb": 127.50, "eur_etb": 138.20}

def get_exchange_rate():
    try:
        resp = requests.get(
            "https://www.nbe.gov.et/monetary-policy/exchange-rates/",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        usd = re.search(r"US\s*Dollar.*?(\d{2,3}[.,]\d{2,4})", resp.text, re.I | re.S)
        eur = re.search(r"Euro.*?(\d{2,3}[.,]\d{2,4})", resp.text, re.I | re.S)
        if usd and eur:
            u = float(usd.group(1).replace(",", "."))
            e = float(eur.group(1).replace(",", "."))
            if 50 < u < 300 and 50 < e < 300:
                log.info("NBE live rates: USD=%.2f EUR=%.2f", u, e)
                return {"usd_etb": round(u, 2), "eur_etb": round(e, 2)}
    except Exception as ex:
        log.warning("NBE fetch failed: %s — using fallback", ex)
    return FALLBACK

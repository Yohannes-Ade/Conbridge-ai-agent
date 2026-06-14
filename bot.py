"""
ConBridge Daily Construction Price Bot
======================================
Posts daily Ethiopian construction material prices to a Telegram channel.
Schedule: Every day at 07:00 AM Addis Ababa time (EAT = UTC+3)

Usage:
    python bot.py               # Run once immediately (for testing)
    python bot.py --schedule    # Run on daily schedule
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.constants import ParseMode

from scrapers.cement import scrape_cement_prices
from scrapers.steel import scrape_steel_prices
from scrapers.aggregates import scrape_aggregate_prices
from scrapers.exchange_rate import get_exchange_rate
from scrapers.fuel import scrape_fuel_prices

# ── Configuration ─────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_ID  = os.getenv("TELEGRAM_CHANNEL_ID", "@conbridge")   # or numeric chat ID
TIMEZONE    = "Africa/Addis_Ababa"
POST_HOUR   = 7    # 7:00 AM EAT
POST_MINUTE = 0

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# ── Message Formatter ─────────────────────────────────────────────────────────
def build_message(cement, steel, aggregates, exchange, fuel) -> str:
    """Build the daily price update message in Telegram MarkdownV2 format."""
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).strftime("%B %d, %Y")

    lines = []
    lines.append(f"📦 *ConBridge Daily Price Update*")
    lines.append(f"🗓 _{today} — Addis Ababa Market_")
    lines.append("")

    # Cement
    lines.append("🏗 *CEMENT \\(ETB/quintal\\)*")
    if cement:
        for item in cement:
            lines.append(f"  • {escape(item['name'])} — *{escape(str(item['price']))} ETB*")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    # Steel
    lines.append("🔩 *REINFORCEMENT STEEL \\(ETB/ton\\)*")
    if steel:
        for item in steel:
            lines.append(f"  • {escape(item['name'])} — *{escape(str(item['price']))} ETB*")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    # Aggregates
    lines.append("🪨 *AGGREGATES \\(ETB/m³\\)*")
    if aggregates:
        for item in aggregates:
            lines.append(f"  • {escape(item['name'])} — *{escape(str(item['price']))} ETB*")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    # Fuel
    lines.append("⛽ *FUEL \\(ETB/litre\\)*")
    if fuel:
        for item in fuel:
            lines.append(f"  • {escape(item['name'])} — *{escape(str(item['price']))} ETB*")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    # Exchange rate
    lines.append("💱 *EXCHANGE RATE*")
    if exchange:
        lines.append(f"  • 1 USD = *{escape(str(exchange['usd_etb']))} ETB* \\(NBE\\)")
        lines.append(f"  • 1 EUR = *{escape(str(exchange['eur_etb']))} ETB* \\(NBE\\)")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("─────────────────────────")
    lines.append("📡 _Sources: Supplier surveys, Telegram market channels, NBE_")
    lines.append("📢 _Post an ad: \\+251917473701_")
    lines.append("🔔 _Join: @con\\_bridge_")

    return "\n".join(lines)


def escape(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


# ── Main Post Function ────────────────────────────────────────────────────────
async def post_daily_prices():
    log.info("Starting daily price collection...")

    # Gather all data (each scraper returns a list of dicts or None on failure)
    cement     = scrape_cement_prices()
    steel      = scrape_steel_prices()
    aggregates = scrape_aggregate_prices()
    exchange   = get_exchange_rate()
    fuel       = scrape_fuel_prices()

    message = build_message(cement, steel, aggregates, exchange, fuel)

    log.info("Sending message to channel %s", CHANNEL_ID)
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    log.info("Message sent successfully.")


# ── Entry Point ───────────────────────────────────────────────────────────────
async def main():
    run_now = "--schedule" not in sys.argv

    if run_now:
        log.info("Running in immediate/test mode...")
        await post_daily_prices()
    else:
        log.info("Running in scheduled mode — will post at %02d:%02d EAT daily.", POST_HOUR, POST_MINUTE)
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        scheduler.add_job(
            post_daily_prices,
            trigger="cron",
            hour=POST_HOUR,
            minute=POST_MINUTE,
        )
        scheduler.start()
        # Keep the process alive
        try:
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            log.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())

"""
ConBridge Daily Construction Price Bot
Posts daily Ethiopian construction material prices to a Telegram channel.
Schedule: Every day at 07:00 AM Addis Ababa time (EAT = UTC+3)

Usage:
    python bot.py               # Run once immediately (for testing)
    python bot.py --schedule    # Run on daily schedule (Railway production)

Required environment variables (Railway Variables tab):
    TELEGRAM_BOT_TOKEN   - Your bot token from @BotFather
    TELEGRAM_CHANNEL_ID  - e.g. @con_bridge or numeric chat ID
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
BOT_TOKEN  = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@con_bridge")
TIMEZONE   = "Africa/Addis_Ababa"
POST_HOUR  = 7
POST_MINUTE = 0

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# ── Message Builder (HTML — no escaping headaches) ────────────────────────────
def build_message(cement, steel, aggregates, exchange, fuel) -> str:
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).strftime("%B %d, %Y")

    lines = []
    lines.append("📦 <b>ConBridge Daily Price Update</b>")
    lines.append(f"🗓 <i>{today} — Addis Ababa Market</i>")
    lines.append("")

    lines.append("🏗 <b>CEMENT (ETB/quintal)</b>")
    if cement:
        for item in cement:
            lines.append(f"  • {item['name']} — <b>{item['price']} ETB</b>")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("🔩 <b>REINFORCEMENT STEEL (ETB/ton)</b>")
    if steel:
        for item in steel:
            lines.append(f"  • {item['name']} — <b>{item['price']} ETB</b>")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("🪨 <b>AGGREGATES (ETB/m³)</b>")
    if aggregates:
        for item in aggregates:
            lines.append(f"  • {item['name']} — <b>{item['price']} ETB</b>")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("⛽ <b>FUEL (ETB/litre)</b>")
    if fuel:
        for item in fuel:
            lines.append(f"  • {item['name']} — <b>{item['price']} ETB</b>")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("💱 <b>EXCHANGE RATE</b>")
    if exchange:
        lines.append(f"  • 1 USD = <b>{exchange['usd_etb']} ETB</b> (NBE)")
        lines.append(f"  • 1 EUR = <b>{exchange['eur_etb']} ETB</b> (NBE)")
    else:
        lines.append("  • Data unavailable today")
    lines.append("")

    lines.append("─────────────────────────")
    lines.append("📡 <i>Sources: Supplier surveys, NBE</i>")
    lines.append("📢 <i>Post an ad: +251917473701</i>")
    lines.append("🔔 <i>Join: @con_bridge</i>")

    return "\n".join(lines)


# ── Main Post Function ────────────────────────────────────────────────────────
async def post_daily_prices():
    log.info("Starting daily price collection...")

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
        parse_mode=ParseMode.HTML,
    )
    log.info("Message sent successfully.")


# ── Entry Point ───────────────────────────────────────────────────────────────
async def main():
    run_now = "--schedule" not in sys.argv

    if run_now:
        log.info("Running in immediate/test mode...")
        await post_daily_prices()
    else:
        log.info(
            "Running in scheduled mode — will post at %02d:%02d EAT daily.",
            POST_HOUR, POST_MINUTE,
        )
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        scheduler.add_job(
            post_daily_prices,
            trigger="cron",
            hour=POST_HOUR,
            minute=POST_MINUTE,
        )
        scheduler.start()
        log.info("Scheduler started. Bot is running...")
        try:
            while True:
                await asyncio.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            log.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())

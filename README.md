# ConBridge Daily Price Bot — Setup & Deployment Guide

## What this bot does
Posts a formatted daily construction material price update to your Telegram
channel (@conbridge) every morning at 7:00 AM Addis Ababa time.

Prices covered:
- Cement (ETB/quintal) — Derba, Messebo, Mugher, etc.
- Reinforcement steel/rebar (ETB/ton) — by diameter
- Aggregates (ETB/m³) — gravel, sand, crushed stone
- Fuel (ETB/litre) — petrol, diesel, kerosene
- Exchange rates (NBE official) — USD/ETB, EUR/ETB

---

## Step 1 — Create your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Give it a name: `ConBridge Price Bot`
4. Give it a username: `conbridge_price_bot` (must end in `bot`)
5. Copy the **API token** — looks like: `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Step 2 — Add the bot to your channel

1. Open your Telegram channel (@conbridge)
2. Go to **Manage Channel → Administrators**
3. Add your new bot as admin
4. Enable: **Post Messages** permission
5. Save

---

## Step 3 — Set up the server

### Option A: Free tier on Railway.app (recommended for beginners)
1. Create account at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Upload this project folder or connect your GitHub
4. Add environment variables in Railway dashboard (see Step 4)
5. Done — Railway keeps it running 24/7

### Option B: VPS (DigitalOcean, Hetzner, etc.)
```bash
# On your server (Ubuntu 22.04):
git clone <your-repo> /home/ubuntu/conbridge_bot
cd /home/ubuntu/conbridge_bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
nano .env   # fill in your token and channel ID

# Test immediately
export $(cat .env | xargs)
python bot.py

# Set up as a system service (runs on boot, auto-restarts)
sudo cp conbridge-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable conbridge-bot
sudo systemctl start conbridge-bot

# Check it's running
sudo systemctl status conbridge-bot
sudo journalctl -u conbridge-bot -f
```

---

## Step 4 — Environment variables

Create a `.env` file (copy from `.env.example`):

```
TELEGRAM_BOT_TOKEN=7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_CHANNEL_ID=@conbridge
```

---

## Step 5 — Test the bot

```bash
# Activate venv
source venv/bin/activate

# Load environment
export $(cat .env | xargs)

# Run once (test mode — sends immediately)
python bot.py

# Run on schedule (7 AM daily)
python bot.py --schedule
```

---

## How prices are collected

| Category | Primary Source | Fallback |
|---|---|---|
| Cement | @con_bridge channel posts | Static estimates |
| Steel | @con_bridge channel posts | Static estimates |
| Aggregates | @con_bridge channel posts | Static estimates |
| Fuel | Ethiopian news sites | Last known govt price |
| Exchange rate | NBE website | open.er-api.com |

### Adding more sources
Each scraper is a separate file in the `scrapers/` folder.
To add a new source, edit the relevant file and add a new function
following the same pattern as the existing ones.

---

## Updating fallback prices manually

When the market shifts significantly, update the fallback prices in each scraper:
- `scrapers/cement.py` → `get_fallback_prices()`
- `scrapers/steel.py` → `get_fallback_prices()`
- `scrapers/aggregates.py` → `get_fallback_prices()`
- `scrapers/fuel.py` → `get_fallback_prices()`

---

## File structure

```
conbridge_bot/
├── bot.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── conbridge-bot.service   # Systemd service (Linux deployment)
├── scrapers/
│   ├── __init__.py
│   ├── cement.py           # Cement price scraper
│   ├── steel.py            # Steel/rebar price scraper
│   ├── aggregates.py       # Aggregate price scraper
│   ├── exchange_rate.py    # NBE exchange rate fetcher
│   └── fuel.py             # Fuel price scraper
├── logs/                   # Log files (auto-created)
└── data/                   # Reserved for price history cache
```

---

## Upgrading to AI-powered mode (Option B)

When you're ready to upgrade, replace the scrapers with a Claude API agent
that intelligently searches multiple sources, understands Amharic text,
and generates richer summaries. Ask Claude to help you build Option B.

import os
import discord
from discord import app_commands
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from config import MAX_PRICE, MIN_DISCOUNT, NOTIFY_LOGIC, QUALITY_GOOD
from scraper import fetch_all_wines
from vintage_checker import check_vintage
from price_checker import check_price
from notifier import send_wines

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("WINE_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

CATEGORY_ALIASES = {
    "riesling": "Riesling",
    "chenin": "Chenin Blanc",
    "dessert": "Dessert Wine",
}

async def run_scan(scan_type="Scheduled", category_filter=None, limit=None):
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print(f"Could not find channel {CHANNEL_ID}")
        return

    label = f"{scan_type} scan" + (f" [{category_filter}]" if category_filter else "")
    await channel.send(f"🔍 **{label} starting...** Fetching WineBid listings...")

    wines = fetch_all_wines()

    if category_filter:
        wines = [w for w in wines if w['category'].lower() == category_filter.lower()]

    await channel.send(f"Found {len(wines)} wines under ${MAX_PRICE}. Checking vintage quality & pricing...")

    results = []
    for wine in wines:
        vintage_quality = check_vintage(wine)
        price_passes, discount_pct, market_price, price_source = check_price(wine, MIN_DISCOUNT)
        vintage_passes = vintage_quality in QUALITY_GOOD

        if NOTIFY_LOGIC == "OR":
            should_notify = vintage_passes or price_passes
        else:
            should_notify = vintage_passes and price_passes

        if should_notify:
            results.append((wine, vintage_quality, discount_pct, market_price, price_source))

    if limit:
        results = results[:limit]

    await send_wines(channel, results, label)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    # Run every Sunday at 7pm Pacific Time
    scheduler.add_job(
        lambda: bot.loop.create_task(run_scan("Scheduled Sunday")),
        CronTrigger(day_of_week='sun', hour=19, minute=0, timezone='America/Los_Angeles')
    )
    scheduler.start()
    print("Scheduler active — runs every Sunday at 7pm PT")

@bot.tree.command(name="winecheck", description="Scan WineBid for matching wines")
@app_commands.describe(
    category="Filter by grape: riesling, chenin, or dessert (default: all)",
    limit="Max number of results to show (useful for testing)"
)
async def winecheck_command(interaction: discord.Interaction, category: str = None, limit: int = None):
    category_filter = CATEGORY_ALIASES.get(category.lower()) if category else None
    if category and not category_filter:
        await interaction.response.send_message(f"Unknown category '{category}'. Use: riesling, chenin, or dessert.")
        return
    await interaction.response.send_message("Scan started! Results will appear in #wine shortly.")
    await run_scan("Manual", category_filter=category_filter, limit=limit)

bot.run(TOKEN)

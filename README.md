# AuctionWineAlert 🍷

I used to manually check every Sunday at 7pm what good wines had become available on WineBid. Thousands of listings, one me. So I built a bot to do the work for me.

AuctionWineAlert scans WineBid automatically and posts qualifying wines to your Discord server's **#wine** channel — or whenever you feel like checking with `/winecheck`.

## Wine criteria

- **Categories:** Chenin Blanc, Riesling, Dessert Wine
- **Max price:** $50 (WineBid listing price)
- **Deal threshold:** ≥40% discount vs Vivino market price
- **Notifies if EITHER:** good/great/legendary vintage year OR ≥40% discount

## Discord commands

| Command | Description |
|---|---|
| `/winecheck` | Scan all categories |
| `/winecheck riesling` | Riesling only |
| `/winecheck chenin` | Chenin Blanc only |
| `/winecheck dessert` | Dessert Wine only |
| `/winecheck riesling 5` | Riesling, max 5 results |

## How vintage quality works

Vintage ratings are stored in `data/vintages.csv` — every year from 1980–2025 is pre-populated for Riesling, Chenin Blanc, and Dessert Wine regions. When a wine's vintage isn't in the file, the bot searches online and saves the result automatically.

## Stack

- Python 3
- discord.py
- BeautifulSoup (WineBid scraping)
- Vivino (market price lookup)
- APScheduler (Sunday 7pm PT scheduler)
- Hosted on Railway

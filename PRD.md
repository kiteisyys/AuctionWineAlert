# AuctionWineAlert — Product Requirements Document

## What is this?
A Discord bot that monitors wine auction sites and alerts a private Discord server when wines matching specific criteria appear. Built for personal use to surface good deals from thousands of listings without manual browsing.

## Phase 1: WineBid
WineBid publishes a new auction list every Sunday at 7pm PT. The bot runs automatically at that time and can also be triggered on-demand via a Discord command.

### Wine criteria
- **Categories:** Chenin Blanc, Riesling, Dessert Wine (scraped by WineBid category)
- **Max price:** $50 (WineBid listing price)
- **Deal threshold:** ≥40% discount vs Wine Searcher average market price
- **Notify if EITHER passes:** good/great vintage year OR ≥40% discount

### Settings (easy to adjust)
- `MAX_PRICE = 50` — max WineBid listing price
- `MIN_DISCOUNT = 0.40` — minimum discount vs market price (40%)
- `NOTIFY_LOGIC = "OR"` — notify if vintage OR price passes ("AND" to require both)
- `CATEGORIES = ["Chenin Blanc", "Riesling", "Dessert Wine"]`

### Filtering logic (in order)
1. Scrape WineBid by category (Chenin Blanc, Riesling, Dessert Wine sections)
2. Drop anything over $50
3. Check vintage quality (local CSV first → web search fallback → save result)
4. Check price vs Wine Searcher (Google fallback if not found)
5. Post to Discord #wine channel if either criteria passes

### Discord notification format
Each matching wine gets its own message with:
- Wine name, vintage year, WineBid price
- Market price reference + discount %
- Vintage quality rating
- Direct link to WineBid listing

### On-demand command
Users can type `/check` in Discord to trigger an immediate scan outside of the Sunday schedule.

## Phase 2: K&L Wine
To be defined later.

## Vintage quality reference
Stored in `data/vintages.csv`. Format:
```
grape,region,year,quality,source,notes
Riesling,Mosel,1990,legendary,Wine Advocate,
Chenin Blanc,Loire,2017,average,Wine Searcher,
```

Quality values: `legendary`, `great`, `good`, `average`, `poor`, `unknown`

Edited via terminal commands and committed to git — never edited directly to avoid formatting errors.

## Hosting
- Platform: Railway (free tier, ~$0–5/month)
- Runs 24/7 to handle on-demand Discord commands
- Scheduled job every Sunday 7pm PT

## Out of scope (for now)
- Multi-user support
- User-configurable criteria
- K&L Wine and other sites
- Bidding or purchasing functionality

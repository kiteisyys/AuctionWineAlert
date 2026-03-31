# === SETTINGS — safe to adjust ===
MAX_PRICE = 50           # max WineBid listing price in USD
MIN_DISCOUNT = 0.40      # minimum discount vs market price (0.40 = 40%)
NOTIFY_LOGIC = "OR"      # "OR" = notify if vintage OR price passes, "AND" = require both

QUALITY_GOOD = {"good", "great", "legendary"}  # vintages that trigger notification

WINEBID_BASE = "https://www.winebid.com"

WINEBID_CATEGORIES = {
    "Riesling": f"{WINEBID_BASE}/BuyWine/Items/Riesling/17763",
    "Dessert Wine": f"{WINEBID_BASE}/BuyWine/Items/Dessert-Wine/14745",
    "Chenin Blanc": None,  # searched by keyword since no direct category URL
}

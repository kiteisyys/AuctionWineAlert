import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def search_wine_searcher(wine_name, vintage):
    query = re.sub(r'[^\w\s]', '', wine_name).strip()
    query = re.sub(r'\s+', '+', query)
    url = f"https://www.wine-searcher.com/find/{query}/{vintage}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')

        # try known price selectors
        for selector in ['.average-price', '[class*="average"]', '[class*="avg-price"]', '.price-avg']:
            tag = soup.select_one(selector)
            if tag:
                match = re.search(r'[\d,]+\.?\d*', tag.get_text())
                if match:
                    return float(match.group().replace(',', '')), 'Wine Searcher'

        # fallback: grab all dollar amounts on the page and take median
        prices = [float(p.replace(',', '')) for p in re.findall(r'\$([\d,]+(?:\.\d{2})?)', resp.text)
                  if 5 < float(p.replace(',', '')) < 5000]
        if prices:
            prices.sort()
            return prices[len(prices) // 2], 'Wine Searcher (estimated)'

    except Exception as e:
        print(f"Wine Searcher error for '{wine_name}': {e}")

    return None, None

def google_price_fallback(wine_name, vintage):
    query = f"{wine_name} {vintage} wine price"
    try:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": query},
            headers=HEADERS,
            timeout=10
        )
        prices = [float(p.replace(',', '')) for p in re.findall(r'\$([\d,]+(?:\.\d{2})?)', resp.text)
                  if 5 < float(p.replace(',', '')) < 5000]
        if prices:
            prices.sort()
            return prices[len(prices) // 2], 'Google search'
    except Exception as e:
        print(f"Google price fallback error: {e}")
    return None, None

def check_price(wine, min_discount):
    """Returns (passes, discount_pct, market_price, source)"""
    name = wine['name']
    vintage = wine.get('vintage', '')
    bid_price = wine['price']

    market_price, source = search_wine_searcher(name, vintage)

    if market_price is None:
        market_price, source = google_price_fallback(name, vintage)

    if market_price is None:
        return True, None, None, 'unverified'  # no price data, notify anyway

    discount = (market_price - bid_price) / market_price
    passes = discount >= min_discount
    return passes, round(discount * 100, 1), market_price, source

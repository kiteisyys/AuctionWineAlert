import re
from curl_cffi import requests as curl_requests

def search_vivino(wine_name, vintage):
    """Search Vivino for market prices — returns median of 750ml listings"""
    query = re.sub(r'[^\w\s]', ' ', wine_name).strip()
    if vintage:
        query = f"{query} {vintage}"
    try:
        resp = curl_requests.get(
            "https://www.vivino.com/search/wines",
            params={"q": query},
            impersonate="chrome110",
            timeout=15
        )
        if resp.status_code != 200:
            return None, None

        # try structured extraction: volume_ml paired with prices array
        pairs = re.findall(
            r'"volume_ml":(\d+)\}\},"prices":\[{"id":\d+,"merchant_id":\d+,"amount":([\d.]+)',
            resp.text
        )
        prices_750 = []
        if pairs:
            for ml, amount in pairs:
                amt = float(amount)
                if not (5 < amt < 2000):
                    continue
                if ml == '750':
                    prices_750.append(amt)
                elif ml == '375':
                    prices_750.append(amt * 2)

        # fallback: grab all "amount" values in a reasonable range
        if not prices_750:
            all_amounts = [
                float(a) for a in re.findall(r'"amount":([\d.]+)', resp.text)
                if 10 < float(a) < 2000
            ]
            if all_amounts:
                all_amounts.sort()
                return all_amounts[len(all_amounts) // 2], 'Vivino (estimated)'
            return None, None

        prices_750.sort()
        return prices_750[len(prices_750) // 2], 'Vivino'

    except Exception as e:
        print(f"Vivino error for '{wine_name}': {e}")
    return None, None

def check_price(wine, min_discount):
    """Returns (passes, discount_pct, market_price, source)"""
    name = wine['name']
    vintage = wine.get('vintage', '')
    bid_price = wine['price']

    market_price, source = search_vivino(name, vintage)

    if market_price is None:
        return True, None, None, 'unverified'  # no price data, notify anyway

    discount = (market_price - bid_price) / market_price
    passes = discount >= min_discount
    return passes, round(discount * 100, 1), market_price, source

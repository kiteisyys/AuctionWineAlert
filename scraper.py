import requests
from bs4 import BeautifulSoup
import re
from config import WINEBID_CATEGORIES, WINEBID_BASE, MAX_PRICE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_price(price_str):
    try:
        return float(re.sub(r'[^\d.]', '', price_str))
    except Exception:
        return None

def parse_vintage(text):
    match = re.search(r'\b(19|20)\d{2}\b', text)
    return int(match.group()) if match else None

def name_from_url(url):
    """Extract readable wine name from URL slug when link text is empty"""
    slug = url.rstrip('/').split('/')[-1].rstrip('~')
    return re.sub(r'-+', ' ', slug).strip()

def fetch_wines_from_url(url, category):
    wines = []
    page = 1
    while True:
        page_url = f"{url}?page={page}" if page > 1 else url
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"Error fetching {page_url}: {e}")
            break

        soup = BeautifulSoup(resp.text, 'lxml')
        items = soup.select('.item')
        if not items:
            break

        for item in items:
            # there are multiple <a> tags with the same href:
            # [0] = image link, [1] = wine name, [2] = price
            all_links = item.select('a[href*="/BuyWine/Item/"]')
            if not all_links:
                continue

            href = all_links[0].get('href', '')
            item_url = WINEBID_BASE + href if href.startswith('/') else href

            # find the link whose text is the wine name (non-empty, not a price)
            name = ''
            for link in all_links:
                text = link.get_text(strip=True)
                if text and not text.startswith('$') and text.lower() not in ('bid', 'track'):
                    name = text
                    break
            if not name:
                name = name_from_url(item_url)

            # find price — try known classes first, fall back to regex
            price_tag = item.select_one('.price, .currentPrice, .bidPrice')
            if price_tag:
                price_str = price_tag.get_text(strip=True)
            else:
                price_match = re.search(r'\$[\d,]+\.?\d*', item.get_text())
                price_str = price_match.group() if price_match else None

            price = parse_price(price_str) if price_str else None
            vintage = parse_vintage(name) or parse_vintage(item_url)

            if price is None or price > MAX_PRICE:
                continue

            # ratings e.g. "WA92"
            rating_tag = item.select_one('.ratingArea, [class*="rating"]')
            ratings = rating_tag.get_text(strip=True) if rating_tag else None

            # thumbnail from the image inside the first link
            img_tag = all_links[0].select_one('img') if all_links else item.select_one('img')
            thumbnail = img_tag.get('src') or img_tag.get('data-src') if img_tag else None
            if thumbnail and thumbnail.startswith('/'):
                thumbnail = WINEBID_BASE + thumbnail

            wines.append({
                "name": name,
                "price": price,
                "vintage": vintage,
                "url": item_url,
                "category": category,
                "ratings": ratings,
                "thumbnail": thumbnail,
            })

        next_page = soup.select_one('a[rel="next"]') or soup.find('a', string=re.compile(r'next', re.I))
        if not next_page:
            break
        page += 1

    return wines

def fetch_all_wines():
    all_wines = []
    for category, url in WINEBID_CATEGORIES.items():
        wines = fetch_wines_from_url(url, category)
        print(f"Found {len(wines)} {category} wines under ${MAX_PRICE}")
        all_wines.extend(wines)
    return all_wines

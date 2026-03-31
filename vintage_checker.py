import csv
import re
import requests
from pathlib import Path

VINTAGES_FILE = Path(__file__).parent / "data" / "vintages.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

REGION_KEYWORDS = {
    'mosel': 'Mosel', 'rheingau': 'Rheingau', 'rheinhessen': 'Rheinhessen',
    'pfalz': 'Pfalz', 'nahe': 'Nahe', 'germany': 'Germany',
    'alsace': 'Alsace',
    'loire': 'Loire', 'vouvray': 'Loire', 'savennieres': 'Loire', 'anjou': 'Loire',
    'sauternes': 'Bordeaux', 'barsac': 'Bordeaux',
    'tokaj': 'Hungary', 'tokaji': 'Hungary',
    'wachau': 'Austria', 'kremstal': 'Austria', 'austria': 'Austria',
}

def load_vintages():
    vintages = {}
    if not VINTAGES_FILE.exists():
        return vintages
    with open(VINTAGES_FILE, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['grape'].lower().strip(), row['region'].lower().strip(), str(row['year']).strip())
            vintages[key] = row['quality'].lower().strip()
    return vintages

def save_vintage(grape, region, year, quality, source="web search", notes=""):
    rows = []
    if VINTAGES_FILE.exists():
        with open(VINTAGES_FILE, newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))

    rows.append({
        'grape': grape, 'region': region, 'year': str(year),
        'quality': quality, 'source': source, 'notes': notes
    })

    with open(VINTAGES_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['grape', 'region', 'year', 'quality', 'source', 'notes'])
        writer.writeheader()
        writer.writerows(rows)

def extract_region(wine_name):
    name_lower = wine_name.lower()
    for keyword, region in REGION_KEYWORDS.items():
        if keyword in name_lower:
            return region
    return 'Unknown'

def search_vintage_quality(grape, region, year):
    query = f"{grape} {region} {year} vintage quality wine"
    try:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": query},
            headers=HEADERS,
            timeout=10
        )
        text = resp.text.lower()
        if any(w in text for w in ['legendary', 'greatest ever', 'perfect', 'once in a century']):
            return 'legendary'
        elif any(w in text for w in ['exceptional', 'outstanding', 'excellent', 'superb', 'brilliant']):
            return 'great'
        elif any(w in text for w in ['very good', 'good year', 'solid year', 'strong year']):
            return 'good'
        elif any(w in text for w in ['average', 'mixed', 'difficult', 'challenging', 'uneven']):
            return 'average'
        elif any(w in text for w in ['poor', 'bad year', 'disappointing', 'weak', 'failure']):
            return 'poor'
        else:
            return 'unknown'
    except Exception as e:
        print(f"Vintage search error: {e}")
        return 'unknown'

def check_vintage(wine):
    if not wine.get('vintage'):
        return 'unknown'

    grape = wine['category']
    region = extract_region(wine['name'])
    year = str(wine['vintage'])

    vintages = load_vintages()
    key = (grape.lower(), region.lower(), year)

    if key in vintages:
        return vintages[key]

    # not in local file — search online and save result
    quality = search_vintage_quality(grape, region, year)
    save_vintage(grape, region, year, quality)
    print(f"Saved new vintage: {grape} {region} {year} → {quality}")
    return quality

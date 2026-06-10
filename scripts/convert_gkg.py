import csv
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from article_store import append_new_articles

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

input_csv = SCRIPT_DIR / "data" / "20260609030000.gkg.csv"
output_json = PROJECT_DIR / "public" / "data" / "gdeltArticles.json"

columns = [
    "GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName",
    "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes",
    "Locations", "V2Locations", "Persons", "V2Persons",
    "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM",
    "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds",
    "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"
]

BAD_DOMAINS_FILE = PROJECT_DIR / "config" / "bad_domains.txt"

def load_bad_domains():
    if not BAD_DOMAINS_FILE.exists():
        return set()

    with BAD_DOMAINS_FILE.open("r", encoding="utf-8") as file:
        return {
            clean_domain(line.strip())
            for line in file
            if line.strip() and not line.strip().startswith("#")
        }

BAD_DOMAINS = load_bad_domains()

def clean_domain(domain):
    domain = domain.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain

def get_domain(url):
    return clean_domain(urlparse(url).netloc)


def is_bad_source(url):
    return get_domain(url) in BAD_DOMAINS


def parse_locations(location_string):
    locations = []

    if not location_string:
        return locations

    for item in location_string.split(";"):
        parts = item.split("#")

        if len(parts) >= 8:
            name = parts[1]
            country = parts[2]
            lat = parts[5]
            lng = parts[6]

            if lat and lng:
                locations.append({
                    "name": name,
                    "country": country,
                    "lat": float(lat),
                    "lng": float(lng)
                })

    return locations


def title_from_url(url):

    decoded_url = unquote(url)

    slug = decoded_url.rstrip("/").split("/")[-1]

    title = (
        slug
        .replace("-", " ")
        .replace("_", " ")
        .replace(".html", "")
        .replace(".cms", "")
    )

    return title.strip()


articles = []

with input_csv.open("r", encoding="utf-8", errors="replace", newline="") as file:
    reader = csv.DictReader(file, fieldnames=columns, delimiter="\t")

    articles_by_url = {}

    for row in reader:
        url = row["DocumentIdentifier"]
        if not url:
            continue

        if is_bad_source(url):
            continue

        source = row["SourceCommonName"] or urlparse(url).netloc
        locations = parse_locations(row["V2Locations"])

        if url not in articles_by_url:
            articles_by_url[url] = {
                "id": row["GKGRECORDID"],
                "title": title_from_url(url),
                "source": source,
                "date": row["DATE"],
                "category": (row["Themes"] or "").split(";")[0],
                "tone": row["V2Tone"],
                "url": url,
                "locations": [],
            }

        seen_locations = {
            (loc["name"], loc["lat"], loc["lng"])
            for loc in articles_by_url[url]["locations"]
        }

        for location in locations:
            key = (location["name"], location["lat"], location["lng"])

            if key not in seen_locations:
                articles_by_url[url]["locations"].append(location)
                seen_locations.add(key)

articles = list(articles_by_url.values())

with output_json.open("w", encoding="utf-8") as file:
    json.dump(articles[:200], file, indent=2)

print(f"Wrote {len(articles[:200])} mapped article-location records")

print(f"Generated {len(articles)} records")
print(f"Output file: {output_json}")
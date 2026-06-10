from pathlib import Path
import csv
from urllib.parse import urlparse, unquote

from article_store import append_new_articles

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

CSV_DIR = SCRIPT_DIR / "data"
BAD_DOMAINS_FILE = PROJECT_DIR / "config" / "bad_domains.txt"

columns = [
    "GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName",
    "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes",
    "Locations", "V2Locations", "Persons", "V2Persons",
    "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM",
    "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds",
    "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"
]


def clean_domain(domain):
    domain = domain.lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def get_domain(url):
    return clean_domain(urlparse(url).netloc)


def load_bad_domains():
    if not BAD_DOMAINS_FILE.exists():
        return set()

    with BAD_DOMAINS_FILE.open("r", encoding="utf-8") as file:
        return {
            clean_domain(line)
            for line in file.read().splitlines()
            if line.strip() and not line.startswith("#")
        }


BAD_DOMAINS = load_bad_domains()


def is_bad_source(url):
    domain = get_domain(url)
    return domain in BAD_DOMAINS


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
                    "lng": float(lng),
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


def convert_csv(csv_path):
    articles_by_url = {}

    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as file:
        reader = csv.DictReader(file, fieldnames=columns, delimiter="\t")

        for row in reader:
            url = row.get("DocumentIdentifier")

            if not url:
                continue

            if is_bad_source(url):
                continue

            source = row.get("SourceCommonName") or get_domain(url)
            locations = parse_locations(row.get("V2Locations"))

            if url not in articles_by_url:
                articles_by_url[url] = {
                    "id": row.get("GKGRECORDID"),
                    "title": title_from_url(url),
                    "source": source,
                    "date": row.get("DATE"),
                    "category": (row.get("Themes") or "").split(";")[0],
                    "tone": row.get("V2Tone"),
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

    return list(articles_by_url.values())


def main():
    csv_files = sorted(CSV_DIR.glob("*.gkg.csv"))

    if not csv_files:
        print(f"No CSV files found in {CSV_DIR}")
        return

    all_articles = []

    for csv_path in csv_files:
        print(f"Processing {csv_path.name}")
        articles = convert_csv(csv_path)
        all_articles.extend(articles)
        print(f"Found {len(articles)} articles")

    append_new_articles(all_articles)


if __name__ == "__main__":
    main()
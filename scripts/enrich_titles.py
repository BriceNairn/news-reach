import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PROJECT_DIR = Path(__file__).resolve().parent.parent
json_path = PROJECT_DIR / "public" / "data" / "gdeltArticles.json"

MAX_ARTICLES_TO_FIX = 2500
SLEEP_SECONDS = 0.5


def extract_headline(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        if twitter_title and twitter_title.get("content"):
            return twitter_title["content"].strip()

        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        if soup.title:
            return soup.title.get_text(strip=True)

    except Exception as error:
        print(f"Failed: {url} ({error})")

    return None


with json_path.open("r", encoding="utf-8") as file:
    articles = json.load(file)

fixed_count = 0

for article in articles:
    if article.get("title_quality") != "bad":
        continue

    if fixed_count >= MAX_ARTICLES_TO_FIX:
        break

    print(f"Trying: {article['url']}")

    headline = extract_headline(article["url"])

    if headline:
        article["title_original"] = article["title"]
        article["title"] = headline
        article["title_quality"] = "enriched"
        fixed_count += 1
        print(f"Fixed: {headline}")

    time.sleep(SLEEP_SECONDS)

with json_path.open("w", encoding="utf-8") as file:
    json.dump(articles, file, indent=2)

print(f"Fixed {fixed_count} titles")
print(f"Enriched {fixed_count} titles")
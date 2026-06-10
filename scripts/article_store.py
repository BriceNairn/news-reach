import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT_DIR / "public" / "data" / "gdeltArticles.json"
MAX_AGE_DAYS = 7


def load_existing_articles():
    if not OUTPUT.exists():
        return []

    with OUTPUT.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_articles(articles):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def remove_old_articles(articles):
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    kept = []

    for article in articles:
        processed_at = article.get("processed_at")

        if not processed_at:
            continue

        article_time = datetime.fromisoformat(processed_at)

        if article_time >= cutoff:
            kept.append(article)

    return kept


def article_key(article):
    return article.get("url")


def append_new_articles(new_articles):
    existing_articles = load_existing_articles()
    existing_articles = remove_old_articles(existing_articles)

    seen = {
        article_key(article)
        for article in existing_articles
        if article_key(article)
    }

    added = 0

    for article in new_articles:
        article["processed_at"] = datetime.now(timezone.utc).isoformat()

        key = article_key(article)

        if not key or key in seen:
            continue

        existing_articles.append(article)
        seen.add(key)
        added += 1

    save_articles(existing_articles)

    print(f"Added {added} new articles")
    print(f"Total articles kept: {len(existing_articles)}")
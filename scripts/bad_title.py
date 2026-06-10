import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
json_path = PROJECT_DIR / "public" / "data" / "gdeltArticles.json"

def complete_words(title):
    return re.findall(r"[A-Za-z]{3,}", title)

def is_bad_title(title):
    words = complete_words(title)
    lower = title.lower()

    bad_patterns = [
        "story.aspx",
        "article ",
        "article_",
        ".html",
        ".cms",
        "ws6",
        "t202",
    ]

    if len(words) < 3:
        return True

    if any(pattern in lower for pattern in bad_patterns):
        return True

    if re.search(r"id=\d+", lower):
        return True

    if sum(char.isdigit() for char in title) > 5:
        return True

    return False

with json_path.open("r", encoding="utf-8") as file:
    articles = json.load(file)

bad_articles = []

for article in articles:
    title = article.get("title", "")

    if is_bad_title(title):
        article["title_quality"] = "bad"
        bad_articles.append(article)
    else:
        article["title_quality"] = "ok"

with json_path.open("w", encoding="utf-8") as file:
    json.dump(articles, file, indent=2)

print(f"Checked {len(articles)} articles")
print(f"Found {len(bad_articles)} bad titles")
#!/usr/bin/env python3
"""
Daily Security News Generator
- Collects security news from multiple RSS feeds (global + Korean sources)
- Generates daily JSON data files for accumulation
- Updates the news index for the dashboard
- Runs daily at 08:00 KST via GitHub Actions
"""

import json
import os
import re
import sys
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html import unescape

KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime("%Y-%m-%d")
TIMESTAMP = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")

# News source RSS feeds
RSS_FEEDS = {
    "global": {
        "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
        "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
        "SecurityWeek": "https://feeds.feedburner.com/securityweek",
        "CISA Alerts": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "Krebs on Security": "https://krebsonsecurity.com/feed/",
        "Dark Reading": "https://www.darkreading.com/rss.xml",
    },
    "korea": {
        "DailySecu": "https://www.dailysecu.com/rss/allArticle.xml",
        "BoanNews": "http://www.boannews.com/media/news_rss.xml",
        "ETNews Security": "https://rss.etnews.com/Section901.xml",
    },
}

# Security-related keywords for filtering/tagging
TAGS = {
    "ransomware": ["ransomware", "ransom", "encrypt", "decrypt", "lockbit",
                    "blackcat", "clop", "conti", "revil", "phobos"],
    "vulnerability": ["CVE-", "vulnerability", "zero-day", "0-day", "exploit",
                       "patch", "buffer overflow", "RCE", "injection"],
    "zeroday": ["zero-day", "0-day", "0day", "zero day"],
    "phishing": ["phishing", "spear-phishing", "credential", "social engineering"],
    "malware": ["malware", "trojan", "backdoor", "RAT", "botnet", "worm",
                "rootkit", "spyware", "keylogger"],
    "apt": ["APT", "nation-state", "threat actor", "campaign", "espionage"],
    "data_breach": ["data breach", "data leak", "exposed", "leaked",
                     "compromised", "stolen data"],
}

TAG_ICONS = {
    "ransomware": "ransomware",
    "vulnerability": "vulnerability",
    "zeroday": "zero-day",
    "phishing": "phishing",
    "malware": "malware",
    "apt": "APT",
    "data_breach": "data-breach",
}

MAX_ARTICLES_PER_SOURCE = 10
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "news")
INDEX_PATH = os.path.join(DATA_DIR, "news_index.json")
HISTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "DB", "total_news_history.md")


def fetch_rss(url, timeout=15):
    """Fetch and parse RSS feed XML."""
    try:
        req = Request(url, headers={"User-Agent": "SecurityNewsBot/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            return ET.fromstring(resp.read())
    except (URLError, HTTPError, ET.ParseError) as e:
        print(f"  [WARN] Failed to fetch {url}: {e}")
        return None


def clean_html(text):
    """Strip HTML tags and unescape entities."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def detect_tags(title, description):
    """Detect security-related tags from title and description."""
    combined = f"{title} {description}".lower()
    found = []
    for tag_key, keywords in TAGS.items():
        for kw in keywords:
            if kw.lower() in combined:
                found.append(TAG_ICONS[tag_key])
                break
    return found


def parse_articles(root, source_name):
    """Parse RSS XML into article dicts."""
    articles = []
    if root is None:
        return articles

    # Try standard RSS and Atom formats
    items = root.findall(".//item")
    if not items:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        items = root.findall(".//atom:entry", ns)

    for item in items[:MAX_ARTICLES_PER_SOURCE]:
        # RSS format
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        pub_el = item.find("pubDate")

        # Atom format fallback
        if link_el is not None and link_el.text is None:
            href = link_el.get("href", "")
        else:
            href = link_el.text if link_el is not None else ""

        if title_el is None or not href:
            # Try atom namespace
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            title_el = item.find("atom:title", ns) if title_el is None else title_el
            link_el_atom = item.find("atom:link", ns)
            if link_el_atom is not None and not href:
                href = link_el_atom.get("href", "")
            desc_el = item.find("atom:summary", ns) if desc_el is None else desc_el
            pub_el = item.find("atom:updated", ns) if pub_el is None else pub_el

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = href.strip() if href else ""
        description = clean_html(desc_el.text if desc_el is not None and desc_el.text else "")
        pub_date = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

        if not title or not link:
            continue

        tags = detect_tags(title, description)
        article_id = hashlib.md5(link.encode()).hexdigest()[:12]

        articles.append({
            "id": article_id,
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "source": source_name,
            "tags": tags,
        })

    return articles


def collect_all_news():
    """Collect news from all RSS feeds."""
    all_news = {"global": [], "korea": []}

    for region, sources in RSS_FEEDS.items():
        for source_name, url in sources.items():
            print(f"  Fetching [{region}] {source_name}...")
            root = fetch_rss(url)
            articles = parse_articles(root, source_name)
            all_news[region].extend(articles)
            print(f"    -> {len(articles)} articles collected")

    return all_news


def save_daily_json(news_data):
    """Save daily news as JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    daily_file = os.path.join(DATA_DIR, f"news_{TODAY}.json")
    daily_record = {
        "date": TODAY,
        "generated_at": TIMESTAMP,
        "total_articles": len(news_data["global"]) + len(news_data["korea"]),
        "global_count": len(news_data["global"]),
        "korea_count": len(news_data["korea"]),
        "global": news_data["global"],
        "korea": news_data["korea"],
    }

    with open(daily_file, "w", encoding="utf-8") as f:
        json.dump(daily_record, f, ensure_ascii=False, indent=2)

    print(f"  Saved daily news: {daily_file}")
    return daily_record


def update_news_index(daily_record):
    """Update the cumulative news index."""
    index = {"last_updated": TIMESTAMP, "dates": []}

    if os.path.exists(INDEX_PATH):
        try:
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                index = json.load(f)
        except (json.JSONDecodeError, KeyError):
            pass

    # Remove existing entry for today if re-running
    index["dates"] = [d for d in index["dates"] if d["date"] != TODAY]

    # Add today's summary
    index["dates"].insert(0, {
        "date": TODAY,
        "generated_at": TIMESTAMP,
        "total_articles": daily_record["total_articles"],
        "global_count": daily_record["global_count"],
        "korea_count": daily_record["korea_count"],
        "file": f"news_{TODAY}.json",
    })

    # Keep up to 365 days
    index["dates"] = index["dates"][:365]
    index["last_updated"] = TIMESTAMP

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"  Updated news index: {INDEX_PATH}")


def update_history_md(news_data):
    """Append today's news to the cumulative markdown history."""
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)

    header = ""
    existing = ""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            # Keep the header line
            lines = content.split("\n")
            if lines and lines[0].startswith("#"):
                header = lines[0] + "\n\n"
                existing = "\n".join(lines[1:])
            else:
                existing = content
    else:
        header = "# Total Security News History\n\n"

    new_section = f"\n## {TIMESTAMP} Updates\n"

    # Global news
    if news_data["global"]:
        new_section += "### Global Intelligence\n"
        by_source = {}
        for article in news_data["global"]:
            src = article["source"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(article)

        for src, articles in by_source.items():
            new_section += f"#### {src}\n"
            for a in articles[:5]:
                tags_str = " ".join(f"`{t}`" for t in a["tags"]) if a["tags"] else ""
                new_section += f"- **[{a['title']}]({a['link']})**\n"
                if tags_str:
                    new_section += f"  - {tags_str}\n"
                if a["description"]:
                    new_section += f"  - {a['description'][:200]}...\n"
                new_section += "\n"

    # Korea news
    if news_data["korea"]:
        new_section += "### Korea Security\n"
        by_source = {}
        for article in news_data["korea"]:
            src = article["source"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(article)

        for src, articles in by_source.items():
            new_section += f"#### {src}\n"
            for a in articles[:5]:
                tags_str = " ".join(f"`{t}`" for t in a["tags"]) if a["tags"] else ""
                new_section += f"- **[{a['title']}]({a['link']})**\n"
                if tags_str:
                    new_section += f"  - {tags_str}\n"
                if a["description"]:
                    new_section += f"  - {a['description'][:200]}...\n"
                new_section += "\n"

    new_section += "---\n"

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        f.write(header + new_section + "\n" + existing)

    print(f"  Updated history: {HISTORY_PATH}")


def generate_summary_stats(daily_record):
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print(f"  Daily Security News Report - {TODAY}")
    print("=" * 60)
    print(f"  Generated at: {TIMESTAMP}")
    print(f"  Total articles: {daily_record['total_articles']}")
    print(f"    Global: {daily_record['global_count']}")
    print(f"    Korea:  {daily_record['korea_count']}")

    # Count tags
    all_articles = daily_record["global"] + daily_record["korea"]
    tag_counts = {}
    for a in all_articles:
        for t in a.get("tags", []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    if tag_counts:
        print("\n  Tag Distribution:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            print(f"    [{tag}]: {count}")
    print("=" * 60)


def main():
    print(f"\n[Daily Security News Generator]")
    print(f"Date: {TODAY} | Timestamp: {TIMESTAMP}\n")

    print("[1/4] Collecting news from RSS feeds...")
    news_data = collect_all_news()

    print("\n[2/4] Saving daily JSON data...")
    daily_record = save_daily_json(news_data)

    print("\n[3/4] Updating news index...")
    update_news_index(daily_record)

    print("\n[4/4] Updating history markdown...")
    update_history_md(news_data)

    generate_summary_stats(daily_record)

    # Output for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"date={TODAY}\n")
            f.write(f"total_articles={daily_record['total_articles']}\n")
            f.write(f"global_count={daily_record['global_count']}\n")
            f.write(f"korea_count={daily_record['korea_count']}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

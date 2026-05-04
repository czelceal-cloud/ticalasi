#!/usr/bin/env python3
"""ticalasi — 全球科技新闻与资讯大事件自动聚合
零API key, 零成本, 从公开RSS抓取.
"""

import json
import os
import re
import hashlib
import html
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

try:
    import feedparser
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

# ============================================================
# 配置
# ============================================================
OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_ARTICLES = 30  # 最多保留30条

# RSS源 — 全球科技 + 重大事件
RSS_SOURCES = [
    # 科技综合
    ("Hacker News", "https://hnrss.org/frontpage?count=10"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("VentureBeat", "https://feeds.feedburner.com/venturebeat/SZYF"),
    # 开源/开发者
    ("GitHub Blog", "https://github.blog/feed/"),
    ("Dev.to", "https://dev.to/feed"),
    ("FreeCodeCamp", "https://www.freecodecamp.org/news/rss/"),
    # 重大事件/综合
    ("Reuters Tech", "https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best&best-sectors=tech"),
    ("BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("NPR", "https://feeds.npr.org/1019/rss.xml"),
    # AI/ML前沿
    ("Google AI Blog", "http://feeds.feedburner.com/blogspot/gJZg"),
    ("Meta AI", "https://ai.meta.com/blog/feed/"),
]

# ============================================================
# 工具函数
# ============================================================
USER_AGENT = "Mozilla/5.0 (compatible; ticalasi-bot/1.0; +https://ticalasi.com)"


def fetch_rss(url: str):
    """获取并解析RSS源"""
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        resp = urlopen(req, timeout=15)
        data = resp.read()
        return feedparser.parse(data)
    except Exception as e:
        print(f"  ⚠ {url[:60]}: {e}")
        return None


def clean_html(text: str) -> str:
    """去除HTML标签"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()


def parse_date(date_struct) -> str:
    """解析feedparser时间 → YYYY-MM-DD"""
    try:
        dt = datetime(*date_struct[:6], tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def generate_id(url: str) -> str:
    """基于URL生成短ID"""
    return hashlib.md5(url.encode()).hexdigest()[:6]


def get_text(entry, *fields):
    """从entry中取文本字段，支持summary/detail"""
    for f in fields:
        val = entry.get(f) or (entry.get(f + "_detail") and entry[f + "_detail"].value)
        if val:
            return clean_html(val)
    return ""


# ============================================================
# 主逻辑
# ============================================================
def main():
    all_articles = []
    seen_urls = set()

    print(f"ticalasi 新闻聚合器 v1.0")
    print(f"从 {len(RSS_SOURCES)} 个源抓取...")
    print()

    for source_name, url in RSS_SOURCES:
        print(f"📡 {source_name}...", end=" ", flush=True)
        feed = fetch_rss(url)
        if not feed or not feed.entries:
            print("✗")
            continue

        count = 0
        for entry in feed.entries:
            # 取链接
            link = entry.get("link", "")
            if not link or link in seen_urls:
                continue
            seen_urls.add(link)

            # 取标题
            title = get_text(entry, "title")
            if not title or len(title) < 10:
                continue

            # 取摘要
            summary = get_text(entry, "summary", "description", "subtitle")
            if not summary:
                summary = title[:60]
            summary = summary[:300]

            # 取日期
            date = parse_date(entry.get("published_parsed") or entry.get("updated_parsed") or feed.feed.get("updated_parsed"))

            # 取 tags
            tags = []
            for tag in entry.get("tags", []):
                t = tag.get("term", "") or tag.get("label", "")
                if t and t not in tags:
                    tags.append(t)
            if not tags:
                tags.append(source_name)

            article = {
                "id": generate_id(link),
                "title": title,
                "summary": summary,
                "url": link,
                "date": date,
                "source": source_name,
                "tags": tags,
            }
            all_articles.append(article)
            count += 1

        print(f"✓ {count}条")

    # 去重（同URL已去重，再按标题相似去重）
    seen_titles = set()
    unique = []
    for a in all_articles:
        key = a["title"][:40].lower().strip()
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)

    # 按日期排序（最新在前）
    unique.sort(key=lambda a: a["date"], reverse=True)

    # 截取最多
    unique = unique[:MAX_ARTICLES]

    # 编号
    for i, a in enumerate(unique, 1):
        a["id"] = f"{i:03d}"

    print(f"\n{'='*50}")
    print(f"总计: {len(unique)} 条文章")

    # ============================================================
    # 写入 articles.json
    # ============================================================
    articles_path = os.path.join(OUTPUT_DIR, "articles.json")
    with open(articles_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"✅ articles.json 已写入 ({len(unique)}条)")

    # ============================================================
    # 写入 feed.json (Atom/RSS兼容格式)
    # ============================================================
    feed_data = {
        "version": "https://jsonfeed.org/version/1",
        "title": "ticalasi — 全球科技前沿",
        "home_page_url": "https://ticalasi.com",
        "feed_url": "https://ticalasi.com/feed.json",
        "description": "自动聚合全球最新科技资讯与大事件",
        "items": [
            {
                "id": a["id"],
                "url": a["url"],
                "title": a["title"],
                "summary": a["summary"],
                "date_published": a["date"],
                "tags": a["tags"],
                "_source": a["source"],
            }
            for a in unique
        ]
    }
    feed_path = os.path.join(OUTPUT_DIR, "feed.json")
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2)
    print(f"✅ feed.json 已写入 ({len(feed_data['items'])}条)")

    # ============================================================
    # 写入 sitemap.xml
    # ============================================================
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '  <url><loc>https://ticalasi.com/</loc></url>\n'
    for a in unique:
        sitemap += f'  <url><loc>https://ticalasi.com/articles/{a["id"]}</loc></url>\n'
    sitemap += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"✅ sitemap.xml 已写入")

    # ============================================================
    # 输出摘要
    # ============================================================
    print(f"\n{'='*50}")
    print(f"最新文章:")
    for a in unique[:5]:
        print(f"  [{a['date']}] {a['title'][:60]}")
        print(f"         {a['source']} | {', '.join(a['tags'][:3])}")
    if len(unique) > 5:
        print(f"  ... 还有 {len(unique)-5} 条")

    return unique


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""ticalasi AI 资讯内容自动生成器 v2
- 使用 DeepSeek API 生成真实 AI 行业文章
- 生成 feed.json + sitemap.xml + articles.json + HTML 页面
- AI 友好的结构化数据标记
"""

import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from xml.dom import minidom

SITE_URL = "https://ticalasi.com"
NOW = datetime.now(timezone.utc)

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# ---------- AI 文章生成 ----------

TOPICS = [
    "大模型最新动态（GPT、Claude、Llama、Gemini等）",
    "AI Agent/自主系统最新进展",
    "开源AI模型和社区动态",
    "AI推理芯片和算力基础设施",
    "多模态AI（视觉/语音/视频生成）最新突破",
    "AI安全、对齐和监管政策",
    "AI编程/软件工程工具进展",
    "具身智能和机器人AI",
    "AI在医疗/科学/教育领域应用",
    "AI投资和创业公司动态",
]

def generate_article(topic):
    """用 DeepSeek 生成一篇真实感 AI 行业短资讯"""
    if not DEEPSEEK_KEY:
        return None

    prompt = f"""你是一个专业的AI科技记者。请写一篇300-400字的AI行业短资讯，主题是：{topic}。

要求：
1. 写一篇看起来像真实新闻的报道
2. 包含具体的技术术语和细节（让人感觉是真的）
3. 时间设定为{NOW.strftime('%Y年%m月%d日')}前后
4. 风格：中立、专业、信息量大
5. 输出格式：
TITLE: [文章标题]
SUMMARY: [一句话摘要，40-60字]
CONTENT: [正文内容]
TAGS: [标签1, 标签2, 标签3]
AUTHOR: [作者署名]

注意：不要添加免责声明或"这只是虚构的"等说明。直接写。"""

    try:
        body = json.dumps({
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 600
        }).encode()
        req = urllib.request.Request(
            DEEPSEEK_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"]

        # Parse structured output
        title = ""
        summary = ""
        content = ""
        tags = []
        author = "ticalasi 编辑团队"

        for line in text.strip().split("\n"):
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("CONTENT:"):
                content = line.replace("CONTENT:", "").strip()
            elif line.startswith("TAGS:"):
                tags = [t.strip() for t in line.replace("TAGS:", "").split(",")]
            elif line.startswith("AUTHOR:"):
                author = line.replace("AUTHOR:", "").strip()

        if not title and not content:
            # Fallback: use whole text as content
            return None

        return {
            "title": title or "AI行业动态",
            "summary": summary or content[:80] + "...",
            "content": content or text,
            "tags": tags or ["AI"],
            "author": author,
            "date": NOW.strftime("%Y-%m-%d")
        }
    except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
        print(f"⚠️ 文章生成失败: {e}")
        return None


def load_existing_articles():
    """加载已有的文章"""
    try:
        with open("articles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def generate_articles(article_id_start):
    """用 AI 生成文章列表"""
    print(f"🔍 使用 DeepSeek API 生成文章...")

    existing = load_existing_articles()
    existing_titles = {a.get("title", "") for a in existing}

    new_articles = []
    articles = list(existing)  # keep existing

    for topic in TOPICS:
        article = generate_article(topic)
        if article and article.get("title") not in existing_titles:
            article["id"] = f"{article_id_start + len(new_articles):03d}"
            articles.append(article)
            new_articles.append(article)
            print(f"  ✅ [{article['id']}] {article['title'][:50]}...")
            existing_titles.add(article["title"])

    if not new_articles:
        print("  ℹ️ 没有新文章（已有文章覆盖所有主题，或API不可用）")

    return articles[:12]  # max 12 articles


# ---------- 文件生成 ----------

def generate_json_feed(articles):
    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": "ticalasi - AI 前沿资讯",
        "home_page_url": SITE_URL,
        "feed_url": f"{SITE_URL}/feed.json",
        "description": "追踪全球AI技术前沿，提供深度分析与行业洞察",
        "items": [
            {
                "id": f"{SITE_URL}/articles/{a['id']}",
                "url": f"{SITE_URL}/articles/{a['id']}",
                "title": a["title"],
                "content_text": a.get("summary", ""),
                "summary": a.get("summary", ""),
                "date_published": f"{a.get('date', NOW.strftime('%Y-%m-%d'))}T00:00:00Z",
                "tags": a.get("tags", []),
                "authors": [{"name": a.get("author", "ticalasi")}]
            } for a in articles
        ]
    }
    with open("feed.json", "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
    print(f"✅ feed.json — {len(articles)} 篇文章")


def generate_sitemap(articles):
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    pages = [("", "hourly", "1.0"), ("/about", "monthly", "0.5")]
    for a in articles:
        aid = a.get("id", "")
        pages.append((f"/articles/{aid}", "daily", "0.8"))

    for path, freq, priority in pages:
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{SITE_URL}{path}"
        for tag, val in [("changefreq", freq), ("priority", priority)]:
            el = ET.SubElement(url, tag)
            el.text = val

    xml_str = minidom.parseString(ET.tostring(urlset)).toprettyxml(indent="  ")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"✅ sitemap.xml — {len(pages)} 个页面")


def generate_articles_json(articles):
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"✅ articles.json — AI 可读文章数据")


def generate_article_pages(articles):
    os.makedirs("articles", exist_ok=True)
    for a in articles:
        tags_html = " ".join(f'<span class="tag">{t}</span>' for t in a.get("tags", []))
        date_str = a.get("date", NOW.strftime("%Y-%m-%d"))
        author = a.get("author", "ticalasi")
        content_paras = "\n".join(
            f'<p>{p.strip()}</p>' for p in a.get("content", "").split("\n") if p.strip()
        )

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{a['title']} — ticalasi</title>
    <meta name="description" content="{a.get('summary', '')}">
    <link rel="canonical" href="{SITE_URL}/articles/{a['id']}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', system-ui, sans-serif; background: #fafafa; color: #1a1a1a; -webkit-font-smoothing: antialiased; line-height: 1.6; }}
        .container {{ max-width: 720px; margin: 0 auto; padding: 0 24px; }}
        nav {{ display: flex; align-items: center; justify-content: space-between; padding: 20px 0; border-bottom: 1px solid #e8e8e8; margin-bottom: 64px; }}
        .logo {{ font-size: 18px; font-weight: 600; letter-spacing: -0.3px; color: #1a1a1a; text-decoration: none; }}
        .nav-links {{ display: flex; gap: 24px; }}
        .nav-links a {{ font-size: 14px; color: #888; text-decoration: none; }}
        .nav-links a:hover {{ color: #1a1a1a; }}
        .meta {{ font-size: 13px; color: #aaa; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
        .tag {{ font-size: 11px; color: #666; background: #f0f0f0; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
        h1 {{ font-size: 32px; font-weight: 700; letter-spacing: -0.5px; line-height: 1.3; margin-bottom: 24px; }}
        .summary {{ font-size: 16px; color: #888; line-height: 1.6; margin-bottom: 32px; padding-bottom: 32px; border-bottom: 1px solid #e8e8e8; }}
        .content {{ font-size: 15px; color: #444; line-height: 1.8; }}
        .content p {{ margin-bottom: 1em; }}
        footer {{ border-top: 1px solid #e8e8e8; padding: 32px 0; margin-top: 64px; font-size: 13px; color: #aaa; }}
    </style>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"NewsArticle","headline":"{a['title']}","datePublished":"{date_str}","author":{{"@type":"Person","name":"{author}"}}}}
    </script>
</head>
<body>
    <div class="container">
        <nav>
            <a href="/" class="logo">ticalasi</a>
            <div class="nav-links">
                <a href="/">文章</a>
                <a href="/about">关于</a>
            </div>
        </nav>
        <article>
            <div class="meta">
                <span>{date_str}</span>
                {tags_html}
            </div>
            <h1>{a['title']}</h1>
            <p class="summary">{a.get('summary', '')}</p>
            <div class="content">{content_paras}</div>
        </article>
        <footer>&copy; 2026 ticalasi <span style="float:right;">{author}</span></footer>
    </div>
</body>
</html>"""

        with open(f"articles/{a['id']}.html", "w", encoding="utf-8") as f:
            f.write(html)

    print(f"✅ articles/ — {len(articles)} 篇文章页面")


if __name__ == "__main__":
    exist = load_existing_articles()
    start_id = max([int(a.get("id", "0")) for a in exist] + [0]) + 1 if exist else 1

    articles = generate_articles(start_id)
    if articles:
        generate_json_feed(articles)
        generate_sitemap(articles)
        generate_articles_json(articles)
        generate_article_pages(articles)
        print(f"\n🕐 生成时间: {NOW.isoformat()}")
        print(f"✅ ticalasi 内容自动生成完成 — {len(articles)} 篇文章")
    else:
        print("❌ 文章生成为空，未写入任何文件")

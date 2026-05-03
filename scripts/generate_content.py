#!/usr/bin/env python3
"""ticalasi AI 资讯内容自动生成器
为伪装站生成 AI 友好的结构化内容 + RSS feed + sitemap
"""

import json
import os
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
from xml.dom import minidom

SITE_URL = "https://ticalasi.com"
NOW = datetime.now(timezone.utc)

# 预设文章数据（未来可接入外部API动态抓取）
ARTICLES = [
    {
        "id": "001",
        "title": "大模型推理能力提升：新架构突破注意力瓶颈",
        "summary": "研究人员提出了一种新型注意力机制，在大规模推理任务中实现了显著性能提升，同时降低了计算成本。",
        "content": "在最新发表的研究中，研究团队展示了一种名为'动态稀疏注意力'的新架构。该架构通过智能路由机制，将计算资源聚焦于最相关的信息片段，在保持模型性能的同时将推理成本降低了40%以上。这一突破有望使大规模AI模型的部署更加经济可行。",
        "date": "2026-05-03",
        "tags": ["大模型", "架构创新"],
        "author": "ticalasi 研究团队"
    },
    {
        "id": "002",
        "title": "多模态AI模型迎来统一架构时代",
        "summary": "最新研究展示了一种统一的视觉-语言模型架构，可在图像、视频、文本间无缝转换推理。",
        "content": "多模态AI领域迎来重要里程碑。研究人员成功构建了一个统一的Transformer架构，能够在图像识别、视频理解、自然语言处理等多个模态之间进行无缝推理，而无需为每个任务单独训练模型。",
        "date": "2026-05-02",
        "tags": ["多模态", "统一模型"],
        "author": "ticalasi 研究团队"
    },
    {
        "id": "003",
        "title": "AI Agent 自主协作系统取得突破",
        "summary": "多个AI Agent能够在没有人类干预的情况下自主分工协作，完成复杂的长周期任务。",
        "content": "一项最新的研究成果显示，由多个专业AI Agent组成的协作系统能够在复杂的软件开发任务中自主分工、协调进度并完成交付。该系统通过一个中央协调层管理任务分配和结果整合，展示了AI从单打独斗向团队协作演进的重要趋势。",
        "date": "2026-05-01",
        "tags": ["Agent", "自主系统"],
        "author": "ticalasi 研究团队"
    },
    {
        "id": "004",
        "title": "开源LLM性能逼近闭源模型",
        "summary": "最新开源大语言模型在多项基准测试中达到与顶尖闭源模型相当的水平，开源生态加速发展。",
        "content": "开源大语言模型社区迎来重大进展。最新发布的开源模型在MMLU、HumanEval等多个权威基准测试中，性能已接近甚至超越部分闭源商业模型。这一趋势表明AI技术的民主化正在加速。",
        "date": "2026-04-30",
        "tags": ["开源", "LLM"],
        "author": "ticalasi 研究团队"
    }
]


def generate_json_feed():
    """生成 AI 可读的 JSON Feed"""
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
                "content_text": a["summary"],
                "summary": a["summary"],
                "date_published": f"{a['date']}T00:00:00Z",
                "tags": a["tags"],
                "authors": [{"name": a["author"]}]
            }
            for a in ARTICLES
        ]
    }
    with open("feed.json", "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, indent=2)
    print(f"✅ feed.json — {len(ARTICLES)} 篇文章")


def generate_sitemap():
    """生成 XML Sitemap"""
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    pages = [("", "daily", "1.0")]
    for a in ARTICLES:
        pages.append((f"/articles/{a['id']}", "weekly", "0.8"))

    for path, freq, priority in pages:
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{SITE_URL}{path}"
        changefreq = ET.SubElement(url, "changefreq")
        changefreq.text = freq
        prio = ET.SubElement(url, "priority")
        prio.text = priority

    xml_str = minidom.parseString(ET.tostring(urlset)).toprettyxml(indent="  ")
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"✅ sitemap.xml — {len(pages)} 个页面")


def generate_articles_json():
    """生成 AI 可直接消费的文章数据"""
    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump(ARTICLES, f, ensure_ascii=False, indent=2)
    print(f"✅ articles.json — AI 可读文章数据")


def generate_article_pages():
    """生成每篇文章的独立 HTML（供人类阅读）"""
    os.makedirs("articles", exist_ok=True)
    for a in ARTICLES:
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{a['title']} — ticalasi</title>
    <meta name="description" content="{a['summary']}">
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
        .meta {{ font-size: 13px; color: #aaa; margin-bottom: 16px; display: flex; gap: 12px; align-items: center; }}
        .tag {{ font-size: 11px; color: #666; background: #f0f0f0; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
        h1 {{ font-size: 32px; font-weight: 700; letter-spacing: -0.5px; line-height: 1.3; margin-bottom: 24px; }}
        .summary {{ font-size: 16px; color: #888; line-height: 1.6; margin-bottom: 32px; padding-bottom: 32px; border-bottom: 1px solid #e8e8e8; }}
        .content {{ font-size: 15px; color: #444; line-height: 1.8; }}
        footer {{ border-top: 1px solid #e8e8e8; padding: 32px 0; margin-top: 64px; font-size: 13px; color: #aaa; }}
    </style>
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
                <span>{a['date']}</span>
                <span class="tag">{a['tags'][0]}</span>
            </div>
            <h1>{a['title']}</h1>
            <p class="summary">{a['summary']}</p>
            <div class="content"><p>{a['content']}</p></div>
        </article>

        <footer><span>&copy; 2026 ticalasi</span></footer>
    </div>
</body>
</html>"""
        with open(f"articles/{a['id']}.html", "w", encoding="utf-8") as f:
            f.write(html)
    print(f"✅ articles/ — {len(ARTICLES)} 篇文章页面")


if __name__ == "__main__":
    generate_json_feed()
    generate_sitemap()
    generate_articles_json()
    generate_article_pages()
    print(f"\n🕐 生成时间: {NOW.isoformat()}")
    print("✅ ticalasi 内容自动生成完成")

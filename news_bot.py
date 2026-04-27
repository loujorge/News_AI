# -*- coding: utf-8 -*-
import feedparser
import io
import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# --- CONFIGURAÇÃO DE FONTES ---
FEEDS_GENERAL = {
    "The Rundown AI": "https://www.therundown.ai/feed",
    "Ben's Bites": "https://www.bensbites.com/feed"
}

FEEDS_TECH = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Wired AI": "https://www.wired.com/feed/category/ai/latest/rss"
}

HISTORY_FILE = "history.txt"
MAX_AGE_HOURS = 48

ARENA_URL = "https://arena.ai/leaderboard"
ARENA_HEADERS = {"User-Agent": "Mozilla/5.0"}

HARDCODED_DICT = {
    "gemini-3-pro": 'Gemini 3 Pro (Preview)',
    "grok-4.1-thinking": 0,
    "gemini-3-flash": 'Gemini 3 Flash (Preview)',
    "Anthropicclaude-opus-4-5-20251101-thinking-32k": 'Claude Opus 4.5',
    "Anthropicclaude-opus-4-5-20251101": 'Claude Opus 4.5',
    "grok-4.1": 0,
    "gemini-3-flash (thinking-minimal)": 'Gemini 3 Flash (Preview)',
    "gpt-5.1-high": 0,
    "ernie-5.0-0110": 0,
    "Anthropicclaude-sonnet-4-5-20250929-thinking-32k": 'Claude Sonnet 4.5',
    "Anthropicclaude-sonnet-4-5-20250929": 'Claude Sonnet 4.5',
    "MoonshotAIkimi-k2.5-thinking": 0,
    "gemini-2.5-pro": 'Gemini 2.5 Pro',
    "ernie-5.0-preview-1203": 0,
    "Anthropicclaude-opus-4-1-20250805-thinking-16k": 0,
    "Anthropicclaude-opus-4-1-20250805": 0,
    "gpt-4.5-preview-2025-02-27": 0,
    "chatgpt-4o-latest-20250326": 'GPT-4o',
    "glm-4.7": 0,
    "gpt-5.2": 0,
    "gpt-5.2-high": 0,
    "gpt-5.1": 0,
    "gpt-5-high": 0,
    "qwen3-max-preview": 0,
    "o3-2025-04-16": 0,
    "grok-4-1-fast-reasoning": 0,
    "MoonshotAIkimi-k2-thinking-turbo": 0,
    "gpt-5-chat": 0,
    "qwen3-max-2025-09-23": 0,
    "glm-4.6": 0,
    "Anthropicclaude-opus-4-20250514-thinking-16k": 0,
    "deepseek-v3.2-exp": 0,
    "deepseek-v3.2-exp-thinking": 0,
    "qwen3-235b-a22b-instruct-2507": 0,
    "grok-4-fast-chat": 0,
    "deepseek-v3.2-thinking": 0,
    "deepseek-v3.2": 0,
    "deepseek-r1-0528": 0,
    "MoonshotAIkimi-k2-0905-preview": 0,
    "ernie-5.0-preview-1022": 0,
    "MoonshotAIkimi-k2-0711-preview": 0,
    "deepseek-v3.1": 0,
    "deepseek-v3.1-thinking": 0,
    "deepseek-v3.1-terminus": 0,
    "deepseek-v3.1-terminus-thinking": 0,
    "qwen3-vl-235b-a22b-instruct": 0,
    "mistral-large-3": 0,
    "Anthropicclaude-opus-4-20250514": 0,
    "gpt-4.1-2025-04-14": 'GPT-4.1',
    "mistral-medium-2508": 0,
    "grok-3-preview-02-24": 0,
    "grok-4-0709": 0,
    "glm-4.5": 0,
    "gemini-2.5-flash": 0,
    "gemini-2.5-flash-preview-09-2025": 0,
    "grok-4-fast-reasoning": 0,
    "Anthropicclaude-haiku-4-5-20251001": 'Claude Haiku 4.5',
    "o1-2024-12-17": 0,
    "qwen3-235b-a22b-no-thinking": 0,
    "qwen3-next-80b-a3b-instruct": 0,
    "Anthropicclaude-sonnet-4-20250514-thinking-32k": 'Claude Sonnet 4',
    "longcat-flash-chat": 0,
    "qwen3-235b-a22b-thinking-2507": 0,
    "deepseek-r1": 0,
    "amazon-nova-experimental-chat-12-10": 0,
    "qwen3-vl-235b-a22b-thinking": 0,
    "mimo-v2-flash (non-thinking)": 0,
    "deepseek-v3-0324": 0,
    "Tencenthunyuan-vision-1.5-thinking": 0,
    "mai-1-preview": 0,
    "o4-mini-2025-04-16": 0,
    "gpt-5-mini-high": 'GPT-5 mini',
    "Anthropicclaude-sonnet-4-20250514": 'Claude Sonnet 4',
    "Anthropicclaude-3-7-sonnet-20250219-thinking-32k": 0,
    "o1-preview": 0,
    "Tencenthunyuan-t1-20250711": 0,
    "gpt-4.1-mini-2025-04-14": 0,
    "gemini-2.5-flash-lite-preview-09-2025-no-thinking": 0,
    "glm-4.6v": 0,
    "gemini-2.5-flash-lite-preview-06-17-thinking": 0,
    "qwen3-235b-a22b": 0,
    "qwen2.5-max": 0,
    "Anthropicclaude-3-5-sonnet-20241022": 0,
    "Anthropicclaude-3-7-sonnet-20250219": 0,
    "glm-4.5-air": 0,
    "gpt-4o-2024-05-13": 'GPT-4o',
    "gpt-4o-2024-08-06": 'GPT-4o',
    "Anthropicclaude-opus-4-6-thinking": 'Claude Opus 4.6',
    "Anthropicclaude-opus-4-6": 'Claude Opus 4.6',
    "gemini-3.1-pro-preview": 'Gemini 3.1 Pro (Preview)',
    "gpt-5.2-chat-latest-20260210": 'GPT-5.2',
    "Anthropicclaude-opus-4-7": 'Claude Opus 4.7',
    "Anthropicclaude-opus-4-7-thinking": 'Claude Opus 4.7',
}


# ── NEWS HELPERS ──────────────────────────────────────────────────────────────

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_history(new_links):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for link in new_links:
            f.write(link + "\n")

def parse_entry_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None

def is_recent(entry):
    pub_date = parse_entry_date(entry)
    if pub_date is None:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    return pub_date >= cutoff

def fetch_category(feed_dict, history):
    articles = []
    links_to_save = []
    for source, url in feed_dict.items():
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= 3 or entry.link in history or not is_recent(entry):
                continue
            pub_date = parse_entry_date(entry)
            pub_str = pub_date.strftime("%d %b, %H:%M") if pub_date else "Recent"
            articles.append({
                "source": source,
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "Update disponível.")[:180] + "...",
                "date": pub_str
            })
            links_to_save.append(entry.link)
            count += 1
    return articles, links_to_save


# ── ARENA AI HELPERS ─────────────────────────────────────────────────────────

def fetch_arena_df():
    r = requests.get(ARENA_URL, headers=ARENA_HEADERS, timeout=30)
    r.raise_for_status()
    tables = pd.read_html(io.StringIO(r.text))
    if not tables:
        raise RuntimeError("No tables found on Arena leaderboard.")
    expected_any = {"Model", "Overall"}
    for t in tables:
        if expected_any.issubset(set(map(str, t.columns))):
            return t
    return max(tables, key=lambda x: x.shape[1])

def compute_arena_rank1(df):
    model_col = df.columns[0]
    results = []
    for col in df.columns[1:]:
        numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(1e10)
        best_idx = int(numeric_col.argsort()[:1][0])
        model_name = str(df.iloc[best_idx][model_col])
        mapped = HARDCODED_DICT.get(model_name)
        if isinstance(mapped, str):
            model_name = mapped
        results.append({"category": str(col), "model": model_name})
    return results

def fetch_arena_leaders():
    """Returns list of {category, model} for rank-1 per category. Returns [] on failure."""
    try:
        df = fetch_arena_df()
        return compute_arena_rank1(df)
    except Exception as e:
        print(f"⚠️  Arena fetch failed: {e}")
        return []


# ── HTML GENERATION ───────────────────────────────────────────────────────────

def source_color(source):
    colors = {
        "The Rundown AI": ("#ffffff", "#000000"),
        "Ben's Bites":    ("#000000", "#ffdc00"),
        "OpenAI":         ("#10a37f", "#d4f5ec"),
        "DeepMind":       ("#4285f4", "#dbeafe"),
        "VentureBeat AI": ("#e85d04", "#fff0e0"),
        "TechCrunch AI":  ("#ff5500", "#ffede5"),
        "The Verge":      ("#ff3b5c", "#ffe0e6"),
        "Wired AI":       ("#b5179e", "#f5d6f7"),
    }
    return colors.get(source, ("#555", "#eee"))

def generate_news_section_html(title, articles):
    if not articles:
        return ""
    cards = ""
    for art in articles:
        fg, bg = source_color(art["source"])
        cards += f"""
        <article class="card">
            <div class="card-top">
                <span class="badge" style="color:{fg};background:{bg};">{art['source']}</span>
                <span class="pub-date">{art['date']}</span>
            </div>
            <h2><a href="{art['link']}" target="_blank">{art['title']}</a></h2>
            <p class="summary">{art['summary']}</p>
        </article>"""
    return f"""
    <section class="news-section">
        <h2 class="section-title">{title}</h2>
        <div class="grid">{cards}</div>
    </section>"""

def generate_arena_section_html(leaders):
    if not leaders:
        return ""

    now = datetime.now(ZoneInfo("Europe/Lisbon"))
    timestamp = now.strftime("%d %b %Y, %H:%M %Z")

    rows = ""
    for item in leaders:
        rows += f"""
            <tr>
                <td class="cat-cell">{item['category']}</td>
                <td class="model-cell">{item['model']}</td>
            </tr>"""

    return f"""
    <section class="news-section">
        <h2 class="section-title">🏆 Arena AI — Category Leaders</h2>
        <p class="arena-ts">Data collected: <strong>{timestamp}</strong> · Source: <a href="https://arena.ai/leaderboard" target="_blank">arena.ai/leaderboard</a></p>
        <div class="arena-wrap">
            <table class="arena-table">
                <thead>
                    <tr><th>Category</th><th>Top Model</th></tr>
                </thead>
                <tbody>{rows}
                </tbody>
            </table>
        </div>
    </section>"""

def generate_html(general_news, tech_news, arena_leaders):
    now = datetime.now()
    date_str = now.strftime("%d de %B, %Y")

    general_html = generate_news_section_html("🌍 General AI & Trends", general_news)
    tech_html = generate_news_section_html("⚙️ Technical Updates & Research", tech_news)
    arena_html = generate_arena_section_html(arena_leaders)

    if not general_news and not tech_news and not arena_leaders:
        content = '<div class="empty"><h2>Tudo calmo por agora...</h2><p>Estão todos a treinar modelos! 😴</p></div>'
    else:
        content = general_html + tech_html + arena_html

    template = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Devs Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #f5f4f0; --surface: #ffffff; --border: #e2e0da; --text: #1a1916; --muted: #6b6860; }}
        @media (prefers-color-scheme: dark) {{
            :root {{ --bg: #111110; --surface: #1c1b19; --border: #2e2d2a; --text: #f0ede6; --muted: #8a8880; }}
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; padding: 2rem; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: auto; }}
        header {{ margin-bottom: 3rem; border-bottom: 1px solid var(--border); padding-bottom: 2rem; }}
        h1 {{ font-family: 'Syne', sans-serif; font-size: 3rem; line-height: 1; margin: 0; }}
        .section-title {{ font-family: 'Syne', sans-serif; font-size: 1.5rem; margin: 3rem 0 1rem; padding-left: 1rem; border-left: 4px solid var(--text); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem; }}
        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; transition: 0.2s; }}
        .card:hover {{ transform: translateY(-3px); border-color: var(--text); }}
        .card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
        .badge {{ font-size: 0.7rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; }}
        .pub-date {{ font-size: 0.75rem; color: var(--muted); }}
        .card h2 {{ font-size: 1.1rem; margin: 0 0 0.5rem; line-height: 1.3; }}
        .card h2 a {{ color: var(--text); text-decoration: none; }}
        .summary {{ font-size: 0.9rem; color: var(--muted); }}
        .empty {{ text-align: center; padding: 5rem; color: var(--muted); }}

        /* Arena */
        .arena-ts {{ font-size: 0.8rem; color: var(--muted); margin: 0 0 1rem; }}
        .arena-ts a {{ color: var(--muted); }}
        .arena-wrap {{ overflow-x: auto; }}
        .arena-table {{ width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); font-size: 0.9rem; }}
        .arena-table thead {{ background: var(--text); color: var(--bg); }}
        .arena-table th {{ padding: 0.7rem 1.2rem; text-align: left; font-weight: 700; font-family: 'Syne', sans-serif; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .arena-table td {{ padding: 0.6rem 1.2rem; border-top: 1px solid var(--border); }}
        .arena-table tbody tr:hover {{ background: var(--bg); }}
        .cat-cell {{ color: var(--muted); font-size: 0.8rem; width: 35%; }}
        .model-cell {{ font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <p style="text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem; margin-bottom: 0.5rem; color: var(--muted);">Internal Intelligence Report</p>
            <h1>AI DEVS<br>REPORT</h1>
            <p style="margin-top: 1rem;">{date_str}</p>
        </header>
        {content}
    </div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)


# ── SLACK PAYLOAD ─────────────────────────────────────────────────────────────

def build_slack_text(general_news, tech_news, arena_leaders):
    now = datetime.now(ZoneInfo("Europe/Lisbon"))
    date_str = now.strftime("%d %b %Y")
    lines = [f"*🤖 AI Devs Report — {date_str}*\n"]

    if arena_leaders:
        lines.append("*🏆 Arena AI — Category Leaders*")
        for item in arena_leaders:
            lines.append(f"  • *{item['category']}*: {item['model']}")
        lines.append("")

    if general_news:
        lines.append("*🌍 General AI & Trends*")
        for art in general_news:
            lines.append(f"  • <{art['link']}|{art['title']}> _{art['source']}_")
        lines.append("")

    if tech_news:
        lines.append("*⚙️ Technical Updates & Research*")
        for art in tech_news:
            lines.append(f"  • <{art['link']}|{art['title']}> _{art['source']}_")

    return "\n".join(lines)


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    history = get_history()

    gen_articles, gen_links = fetch_category(FEEDS_GENERAL, history)
    tech_articles, tech_links = fetch_category(FEEDS_TECH, history)
    arena_leaders = fetch_arena_leaders()

    generate_html(gen_articles, tech_articles, arena_leaders)
    save_history(gen_links + tech_links)

    slack_text = build_slack_text(gen_articles, tech_articles, arena_leaders)
    with open("slack_payload.txt", "w", encoding="utf-8") as f:
        f.write(slack_text)

    print(f"✅ Report gerado: {len(gen_articles)} generalistas, {len(tech_articles)} técnicas, {len(arena_leaders)} categorias Arena.")

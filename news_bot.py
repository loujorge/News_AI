# -*- coding: utf-8 -*-
import feedparser
import os
from datetime import datetime, timezone, timedelta

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
            try: return datetime(*t[:6], tzinfo=timezone.utc)
            except: pass
    return None

def is_recent(entry):
    pub_date = parse_entry_date(entry)
    if pub_date is None: return True
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

def generate_section_html(title, articles):
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
        </article>
        """
    return f"""
    <section class="news-section">
        <h2 class="section-title">{title}</h2>
        <div class="grid">{cards}</div>
    </section>
    """

def generate_html(general_news, tech_news):
    now = datetime.now()
    date_str = now.strftime("%d de %B, %Y")
    
    general_html = generate_section_html("🌍 General AI & Trends", general_news)
    tech_html = generate_section_html("⚙️ Technical Updates & Research", tech_news)
    
    if not general_news and not tech_news:
        content = '<div class="empty"><h2>Tudo calmo por agora...</h2><p>Estão todos a treinar modelos! \U0001F634</p></div>'
    else:
        content = general_html + tech_html

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
        .section-title {{ font-family: 'Syne', sans-serif; font-size: 1.5rem; margin: 3rem 0 1.5rem; padding-left: 1rem; border-left: 4px solid var(--text); }}
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

if __name__ == "__main__":
    history = get_history()
    
    gen_articles, gen_links = fetch_category(FEEDS_GENERAL, history)
    tech_articles, tech_links = fetch_category(FEEDS_TECH, history)
    
    generate_html(gen_articles, tech_articles)
    save_history(gen_links + tech_links)
    
    print(f"✅ Report gerado: {len(gen_articles)} generalistas, {len(tech_articles)} técnicas.")

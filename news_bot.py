# -*- coding: utf-8 -*-
import feedparser
import os
from datetime import datetime, timezone, timedelta
import time

FEEDS = {
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "OpenAI": "https://openai.com/news/rss.xml",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
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
    """Tenta extrair a data de publicação do artigo."""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None

def is_recent(entry):
    """Retorna True se o artigo foi publicado nas últimas MAX_AGE_HOURS horas."""
    pub_date = parse_entry_date(entry)
    if pub_date is None:
        return True  # sem data, deixa passar por segurança
    cutoff = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    return pub_date >= cutoff

def get_data():
    history = get_history()
    articles = []
    new_links_to_save = []
    slack_text = "*🔥 AI DEVS INTELLIGENCE REPORT*\n\n"

    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= 3:
                break
            if entry.link in history:
                continue
            if not is_recent(entry):
                continue

            pub_date = parse_entry_date(entry)
            pub_str = pub_date.strftime("%d %b %Y, %H:%M UTC") if pub_date else "Data desconhecida"

            articles.append({
                "source": source,
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "Novo update técnico disponível.")[:220] + "...",
                "date": pub_str,
            })
            new_links_to_save.append(entry.link)
            slack_text += f"• *[{source}]* {entry.title}\n<{entry.link}|Link>\n"
            count += 1

    return articles, slack_text, new_links_to_save

def source_color(source):
    colors = {
        "OpenAI":        ("#10a37f", "#d4f5ec"),
        "DeepMind":      ("#4285f4", "#dbeafe"),
        "VentureBeat AI": ("#e85d04", "#fff0e0"),
        "TechCrunch AI":  ("#ff5500", "#ffede5"),
        "The Verge":     ("#ff3b5c", "#ffe0e6"),
        "Wired AI":      ("#b5179e", "#f5d6f7"),
    }
    return colors.get(source, ("#555", "#eee"))

def generate_html(articles):
    now = datetime.now()
    date_str = now.strftime("%d de %B de %Y")
    hour_str = now.strftime("%H:%M UTC")
    count = len(articles)

    cards_html = ""
    for art in articles:
        fg, bg = source_color(art["source"])
        cards_html += f"""
        <article class="card">
            <div class="card-top">
                <span class="badge" style="color:{fg};background:{bg};">{art['source']}</span>
                <span class="pub-date">{art['date']}</span>
            </div>
            <h2><a href="{art['link']}" target="_blank" rel="noopener">{art['title']}</a></h2>
            <p class="summary">{art['summary']}</p>
            <a class="read-btn" href="{art['link']}" target="_blank" rel="noopener">Ler artigo →</a>
        </article>
        """

    sources_legend = ""
    seen = []
    for art in articles:
        if art["source"] not in seen:
            fg, bg = source_color(art["source"])
            sources_legend += f'<span class="legend-dot" style="background:{fg};"></span><span class="legend-name">{art["source"]}</span>'
            seen.append(art["source"])

    # Tratamento do Empty State para evitar erro de encoding com emojis
    content_html = f"<div class='grid'>{cards_html}</div>" if articles else f"""
    <div class="empty">
        <h2>Sem notícias novas</h2>
        <p>Nenhum artigo novo nas últimas 48 horas. Estão todos a treinar modelos! \U0001F634</p>
    </div>
    """

    template = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Intelligence Report · {date_str}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg: #f5f4f0;
            --surface: #ffffff;
            --border: #e2e0da;
            --text: #1a1916;
            --muted: #6b6860;
            --accent: #0f0e0c;
            --font-head: 'Syne', sans-serif;
            --font-body: 'DM Sans', sans-serif;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg: #111110;
                --surface: #1c1b19;
                --border: #2e2d2a;
                --text: #f0ede6;
                --muted: #8a8880;
                --accent: #f0ede6;
            }}
        }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: var(--font-body);
            font-size: 15px;
            line-height: 1.6;
            min-height: 100vh;
            padding: 0 0 5rem;
        }}

        .site-header {{
            border-bottom: 1px solid var(--border);
            padding: 2.5rem 0 2rem;
            margin-bottom: 3rem;
        }}

        .header-inner {{
            max-width: 1080px;
            margin: auto;
            padding: 0 2rem;
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .brand {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .brand-label {{
            font-family: var(--font-head);
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--muted);
        }}

        .brand-title {{
            font-family: var(--font-head);
            font-size: clamp(1.8rem, 4vw, 2.8rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1;
            color: var(--text);
        }}

        .header-meta {{
            text-align: right;
        }}

        .header-meta .date {{
            font-family: var(--font-head);
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--muted);
        }}

        .header-meta .count {{
            font-size: 2rem;
            font-weight: 700;
            font-family: var(--font-head);
            color: var(--text);
            line-height: 1;
        }}

        .header-meta .count-label {{
            font-size: 0.75rem;
            color: var(--muted);
        }}

        .sources-bar {{
            max-width: 1080px;
            margin: 0 auto 2.5rem;
            padding: 0 2rem;
            display: flex;
            align-items: center;
            gap: 0.75rem 1.25rem;
            flex-wrap: wrap;
        }}

        .sources-bar-label {{
            font-size: 0.72rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--muted);
            margin-right: 0.25rem;
        }}

        .legend-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }}

        .legend-name {{
            font-size: 0.78rem;
            color: var(--muted);
        }}

        .grid {{
            max-width: 1080px;
            margin: auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.25rem;
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.4rem 1.5rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: border-color 0.2s, transform 0.2s;
        }}

        .card:hover {{
            border-color: var(--text);
            transform: translateY(-3px);
        }}

        .card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .badge {{
            font-family: var(--font-head);
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 9px;
            border-radius: 20px;
        }}

        .pub-date {{
            font-size: 0.7rem;
            color: var(--muted);
            white-space: nowrap;
        }}

        .card h2 {{
            font-family: var(--font-head);
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.35;
            letter-spacing: -0.01em;
        }}

        .card h2 a {{
            color: var(--text);
            text-decoration: none;
        }}

        .card h2 a:hover {{
            text-decoration: underline;
            text-underline-offset: 3px;
        }}

        .summary {{
            font-size: 0.85rem;
            color: var(--muted);
            line-height: 1.65;
            flex: 1;
        }}

        .read-btn {{
            display: inline-block;
            margin-top: auto;
            font-size: 0.8rem;
            font-weight: 500;
            color: var(--text);
            text-decoration: none;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1px;
            width: fit-content;
            transition: border-color 0.15s;
        }}

        .read-btn:hover {{
            border-color: var(--text);
        }}

        .empty {{
            max-width: 480px;
            margin: 6rem auto;
            text-align: center;
            color: var(--muted);
        }}

        .empty h2 {{
            font-family: var(--font-head);
            font-size: 1.5rem;
            color: var(--text);
            margin-bottom: 0.5rem;
        }}

        footer {{
            max-width: 1080px;
            margin: 4rem auto 0;
            padding: 1.5rem 2rem 0;
            border-top: 1px solid var(--border);
            font-size: 0.75rem;
            color: var(--muted);
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        @media (max-width: 600px) {{
            .header-inner {{ flex-direction: column; align-items: flex-start; }}
            .header-meta {{ text-align: left; }}
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

<header class="site-header">
    <div class="header-inner">
        <div class="brand">
            <span class="brand-label">Curadoria automática para devs</span>
            <h1 class="brand-title">AI Intelligence<br>Report</h1>
        </div>
        <div class="header-meta">
            <div class="date">{date_str} · {hour_str}</div>
            <div class="count">{count}</div>
            <div class="count-label">artigos das últimas 48h</div>
        </div>
    </div>
</header>

<div class="sources-bar">
    <span class="sources-bar-label">Fontes</span>
    {sources_legend}
</div>

{content_html}

<footer>
    <span>AI Intelligence Report · Gerado automaticamente</span>
    <span>Fontes: VentureBeat, OpenAI, DeepMind, TechCrunch, The Verge, Wired</span>
</footer>

</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)

if __name__ == "__main__":
    articles, slack_text, new_links = get_data()
    if articles:
        generate_html(articles)
        save_history(new_links)
        with open("slack_payload.txt", "w", encoding="utf-8") as f:
            f.write(slack_text)
        print(f"✅ {len(articles)} artigos novos nas últimas 48h.")
    else:
        generate_html([])
        with open("slack_payload.txt", "w", encoding="utf-8") as f:
            f.write("Sem notícias novas nas últimas 48h. Estão todos a treinar modelos!")
        print("ℹ️  Sem artigos novos.")

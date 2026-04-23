import feedparser
import os
from datetime import datetime

# Fontes de elite - Adicionei mais 3 de peso
FEEDS = {
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "OpenAI": "https://openai.com/news/rss.xml",
    "DeepMind": "https://deepmind.google/blog/rss.xml",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Wired AI": "https://www.wired.com/feed/category/ai/latest/rss"
}

HISTORY_FILE = "history.txt"

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_history(new_links):
    with open(HISTORY_FILE, "a") as f:
        for link in new_links:
            f.write(link + "\n")

def get_data():
    history = get_history()
    articles = []
    new_links_to_save = []
    slack_text = "*🔥 AI DEVS INTELLIGENCE REPORT*\n\n"
    
    for source, url in FEEDS.items():
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            if count >= 3: break # Máximo 3 por fonte para não inundar
            if entry.link not in history:
                articles.append({
                    "source": source,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get('summary', 'Novo update técnico disponível.')[:200] + "..."
                })
                new_links_to_save.append(entry.link)
                slack_text += f"• *[{source}]* {entry.title}\n<{entry.link}|Link>\n"
                count += 1
    
    return articles, slack_text, new_links_to_save

def generate_html(articles):
    date_str = datetime.now().strftime("%d de %B, %Y")
    cards_html = ""
    
    for art in articles:
        cards_html += f"""
        <div class="card">
            <span class="badge">{art['source']}</span>
            <h2>{art['title']}</h2>
            <p>{art['summary']}</p>
            <a href="{art['link']}" target="_blank">Ler Artigo Completo</a>
        </div>
        """
    
    template = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Intelligence Report</title>
        <style>
            :root {{ --bg: #0b0e14; --card: #151921; --accent: #00f2ff; --text: #e1e1e1; }}
            body {{ background: var(--bg); color: var(--text); font-family: 'Inter', system-ui, sans-serif; margin: 0; padding: 2rem; }}
            .container {{ max-width: 900px; margin: auto; }}
            header {{ border-bottom: 2px solid #222; padding-bottom: 1rem; margin-bottom: 2rem; }}
            h1 {{ color: var(--accent); margin: 0; font-size: 1.8rem; letter-spacing: -1px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }}
            .card {{ background: var(--card); padding: 1.5rem; border-radius: 12px; border: 1px solid #222; transition: transform 0.2s; }}
            .card:hover {{ transform: translateY(-5px); border-color: var(--accent); }}
            .badge {{ background: rgba(0, 242, 255, 0.1); color: var(--accent); padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }}
            h2 {{ font-size: 1.1rem; margin: 10px 0; line-height: 1.4; }}
            p {{ color: #888; font-size: 0.9rem; line-height: 1.6; }}
            a {{ color: var(--accent); text-decoration: none; font-size: 0.85rem; font-weight: bold; border: 1px solid var(--accent); padding: 8px 15px; border-radius: 6px; display: inline-block; margin-top: 10px; }}
            a:hover {{ background: var(--accent); color: var(--bg); }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>AI Intelligence Report</h1>
                <p style="color: #666;">{date_str} • Curadoria Automática para Devs</p>
            </header>
            <div class="grid">{cards_html}</div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f: f.write(template)

if __name__ == "__main__":
    articles, slack_text, new_links = get_data()
    if articles:
        generate_html(articles)
        save_history(new_links)
        with open("slack_payload.txt", "w", encoding="utf-8") as f: f.write(slack_text)
    else:
        with open("slack_payload.txt", "w", encoding="utf-8") as f: f.write("Sem notícias novas hoje. Estão todos a treinar modelos! 😴")

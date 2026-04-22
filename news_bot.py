import feedparser
import os
from datetime import datetime

# Fontes de elite
FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://openai.com/news/rss.xml",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
]

def get_data():
    articles = []
    slack_text = "*🚀 Daily AI News & Briefing*\n\n"
    
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get('summary', 'Clica no link para mais detalhes.')[:250] + "..."
            })
            slack_text += f"• *{entry.title}*\n<{entry.link}|Ler original>\n"
    
    return articles, slack_text

def generate_html(articles):
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    cards = ""
    for art in articles:
        cards += f"""
        <div class="card">
            <h2>{art['title']}</h2>
            <p>{art['summary']}</p>
            <a href="{art['link']}" target="_blank">Ver mais</a>
        </div>
        """
    
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Briefing {date_str}</title>
        <style>
            body {{ font-family: sans-serif; background: #121212; color: white; max-width: 700px; margin: auto; padding: 20px; }}
            h1 {{ color: #00d1b2; border-bottom: 1px solid #333; }}
            .card {{ background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #333; }}
            a {{ color: #00d1b2; text-decoration: none; font-weight: bold; }}
            p {{ color: #aaa; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <h1>Briefing AI - {date_str}</h1>
        {cards}
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)

if __name__ == "__main__":
    articles, slack_text = get_data()
    generate_html(articles)
    
    # Exportar o texto do Slack para o ambiente do GitHub Actions
    with open("slack_payload.txt", "w", encoding="utf-8") as f:
        f.write(slack_text)

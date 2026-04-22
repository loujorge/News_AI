import feedparser
import requests
import os

# Lista de fontes de elite para AI
FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://openai.com/news/rss.xml",
    "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
]

SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')
HISTORY_FILE = "sent_news.txt"

def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_history(links):
    with open(HISTORY_FILE, "a") as f:
        for link in links:
            f.write(link + "\n")

def get_latest_news():
    history = get_history()
    new_links = []
    message_blocks = []
    
    for url in FEEDS:
        print(f"A ler: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]: # 3 de cada fonte
            if entry.link not in history:
                message_blocks.append(f"• *{entry.title}*\n<{entry.link}|Ler artigo>")
                new_links.append(entry.link)

    if not message_blocks:
        return None, []

    final_message = "*🚀 Top Daily AI News for Devs:*\n\n" + "\n\n".join(message_blocks[:8])
    return final_message, new_links

def send_to_slack(text):
    requests.post(SLACK_WEBHOOK, json={"text": text})

if __name__ == "__main__":
    content, links = get_latest_news()
    if content:
        send_to_slack(content)
        save_history(links)
        print(f"Enviadas {len(links)} notícias novas.")
    else:
        print("Sem notícias novas hoje.")

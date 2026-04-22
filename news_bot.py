import feedparser
import requests
import os

# Configurações
# Usando o feed do Hacker News filtrado por AI para ser mais técnico
RSS_URL = "https://hnrss.org/newest?q=AI+OR+LLM+OR+Machine+Learning"
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

def get_latest_news():
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:5] # Pega nas 5 notícias mais recentes
    
    message = "*🚀 Top Daily AI News for Devs:*\n\n"
    
    for entry in entries:
        message += f"• *{entry.title}*\n<{entry.link}|Ler artigo>\n\n"
    
    return message

def send_to_slack(text):
    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK, json=payload)
    if response.status_code == 200:
        print("Notícias enviadas com sucesso!")
    else:
        print(f"Erro ao enviar: {response.status_code}")

if __name__ == "__main__":
    content = get_latest_news()
    send_to_slack(content)

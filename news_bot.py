import feedparser
import requests
import os

# Usando um feed mais estável (TechCrunch AI ou um agregador mais genérico)
RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')

def get_latest_news():
    print(f"A aceder ao feed: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)
    
    # Debug: Ver quantas notícias o script encontrou
    print(f"Notícias encontradas: {len(feed.entries)}")
    
    if not feed.entries:
        return "Nenhuma notícia nova encontrada nas últimas horas. 😴"

    message = "*🚀 Top Daily AI News for Devs:*\n\n"
    
    # Vamos buscar as 5 melhores
    for entry in feed.entries[:5]:
        message += f"• *{entry.title}*\n<{entry.link}|Ler artigo>\n\n"
    
    return message

def send_to_slack(text):
    if not SLACK_WEBHOOK:
        print("ERRO: O Secret SLACK_WEBHOOK_URL não foi encontrado!")
        return

    payload = {"text": text}
    response = requests.post(SLACK_WEBHOOK, json=payload)
    
    if response.status_code == 200:
        print("Enviado para o Slack com sucesso!")
    else:
        print(f"Erro no Slack: {response.status_code} - {response.text}")

if __name__ == "__main__":
    content = get_latest_news()
    send_to_slack(content)

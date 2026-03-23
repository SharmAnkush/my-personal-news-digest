import os
from newsapi import NewsApiClient
import anthropic
import requests
from datetime import datetime

# === CONFIGURE YOUR PREFERENCES HERE ===
KEYWORDS = "AI, technology, science, business, Texas, Plano"  # Change to whatever you want (e.g. "sports, finance, health")
COUNTRY = "us"  # or your preference

# Load keys from GitHub Secrets
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Fetch news
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
today = datetime.utcnow().strftime("%Y-%m-%d")

articles_response = newsapi.get_everything(
    q=KEYWORDS,
    language="en",
    sort_by="publishedAt",
    page_size=20,
    from_param=yesterday,          # ← changed
    to=today                       # optional, but explicit
)


articles = articles_response["articles"]

# Build input for Claude
news_text = ""
for article in articles:
    news_text += f"Title: {article['title']}\n"
    news_text += f"Source: {article['source']['name']}\n"
    news_text += f"Link: {article['url']}\n"
    news_text += f"Description: {article.get('description', '')}\n\n"

# Personalized Claude prompt
prompt = f"""You are my personal news curator. I live in Plano, Texas and care about: {KEYWORDS}.

Create a clean, daily personalized news feed from the articles below.
- Only include articles that match my interests (ignore the rest).
- For each relevant article: **Title** (bold), 2-3 sentence summary, source, and link.
- Start with today's date and "Your Personalized Digest".
- Use clean Markdown formatting.
- Keep the whole digest under 2000 words.

Articles:
{news_text}
"""

# Call Claude (use latest balanced model)
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
response = client.messages.create(
    model="claude-sonnet-4-6",          # fastest + smartest for this in 2026
    max_tokens=2000,
    temperature=0.7,
    messages=[{"role": "user", "content": prompt}]
)

summary = response.content[0].text

# Send to your phone via Telegram
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": summary,
    "parse_mode": "Markdown"
}
requests.post(url, json=payload)

print("✅ Digest sent to Telegram!")

import os
from newsapi import NewsApiClient
import anthropic
import requests
from datetime import datetime, timedelta

# === CONFIGURE YOUR PREFERENCES HERE ===
KEYWORDS = (
    "AI OR artificial intelligence OR LLM OR Grok OR Claude OR GPT "
    "OR technology OR tech OR startup OR venture capital OR funding "
    "OR Tesla OR xAI OR SpaceX OR OpenAI OR Anthropic OR Nvidia "
    "OR electric vehicle OR EV OR autonomous OR robot OR Optimus "
    "OR space OR rocket OR Starlink OR satellite "
    "OR finance OR fintech OR stock OR investment OR economy "
    "OR Texas OR Dallas OR Austin OR Plano"
)
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
- Prioritize articles that clearly match my interests, but if few/no strong matches, include 4–8 of the most relevant/recent ones anyway (even loose connections like general US business/tech/economy, local Texas news, or science broadly).
- Note at the top if you're including "slightly broader but potentially interesting" items.
- For each: **Title** (bold), 2-3 sentence summary in your own words, source, and link.
- Start with today's date (e.g. March 23, 2026) and "Good evening, Ankush! Here's your personalized digest".
- Use clean Markdown formatting with line breaks.
- Keep under 2000 words total.

Articles:
{news_text if news_text else "No articles fetched today — check API key or try later."}
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

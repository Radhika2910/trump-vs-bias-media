import os
import csv
from newsapi import NewsApiClient
from datetime import datetime

API_KEY = '14856857dfeb4ce2a76d8adf4e3e0704'  # Replace with your NewsAPI key

newsapi = NewsApiClient(api_key=API_KEY)

target_countries = ['in', 'us', 'gb', 'pk', 'tr', 'au', 'cn', 'bd', 'lk']

from_date = '2025-04-29'
to_date = datetime.today().strftime('%Y-%m-%d')

# Create outputs directory if it doesn't exist
output_dir = 'outputs'
os.makedirs(output_dir, exist_ok=True)

# Get all sources for English language
sources_response = newsapi.get_sources(language='en')

sources_filtered = [
    source['id'] for source in sources_response['sources']
    if source['country'] in target_countries
]

sources_str = ','.join(sources_filtered)

def fetch_and_save_to_csv(query, filename):
    print(f"Fetching articles for query: '{query}'...")
    all_articles = newsapi.get_everything(
        q=query,
        sources=sources_str,
        from_param=from_date,
        to=to_date,
        language='en',
        sort_by='publishedAt',
        page_size=100,
        page=1
    )
    
    articles = all_articles.get('articles', [])
    if not articles:
        print(f"No articles found for query: {query}")
        return

    filename = "news_api_" + filename
    csv_path = os.path.join(output_dir, filename)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['source_name', 'author', 'title', 'description', 'url', 'publishedAt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for article in articles:
            writer.writerow({
                'source_name': article['source'].get('name', ''),
                'author': article.get('author', ''),
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', '')
            })

    print(f"Saved {len(articles)} articles to {csv_path}")

# Fetch and save for both queries
fetch_and_save_to_csv('pahalgam attack', 'pahalgam_attack_headlines.csv')
fetch_and_save_to_csv('operation sindoor', 'operation_sindoor_headlines.csv')

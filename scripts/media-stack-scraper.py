import requests
from datetime import datetime
import os
import csv
import time

API_KEY = "df2d2a6251a40e68b9cefa95671409d9"
BASE_URL = "http://api.mediastack.com/v1/news"

# Queries to search
queries = ["pahalgam attack", "operation sindoor"]

# Countries (ISO 2-letter codes) to include
countries = ['in', 'us', 'gb', 'pk', 'tr', 'au', 'cn', 'bd', 'lk']

# Date range
from_date = "2025-04-22"
to_date = datetime.today().strftime("%Y-%m-%d")

# Output directory
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

def fetch_articles(query, country, page=1, limit=100):
    params = {
        "access_key": API_KEY,            # API key value
        "countries": country, # Comma-separated countries
        "languages": "en",                # Language filter (English)
        "keywords": query,                # Search query
        "from": from_date,                # Start date
        "to": to_date,                    # End date
        "limit": limit,                   # Max number of articles per request
        "page": page,                     # Page number
    }
    try:
        response = requests.get(BASE_URL, params=params)
        print(f"API Response for query '{query}': {response.status_code}")
        print("Raw Response:", response.text)  # To see the actual API response
        
        response.raise_for_status()  # Will raise an HTTPError for 4xx/5xx responses
        # If rate limit (429), handle by sleeping
        if response.status_code == 429:
            print("Rate limit reached. Sleeping for 60 seconds...")
            time.sleep(60)  # Sleep for 60 seconds before retrying
            return fetch_articles(query, country, page, limit)  # Retry the request
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error for query '{query}': {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Error fetching data for query '{query}': {err}")
    return None

def save_articles_to_csv(filename, articles):
    csv_path = os.path.join(output_dir, filename)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['source_name', 'author', 'title', 'description', 'url', 'publishedAt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            if isinstance(article, dict):
                writer.writerow({
                    'source_name': article.get('source', ''),
                    'author': article.get('author', ''),
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'publishedAt': article.get('published_at', '')
                })

    print(f"Saved {len(articles)} articles to {csv_path}")

def main():
    for query in queries:
        print(f"\nFetching articles for: '{query}'")
        all_articles = []
        
        # MediaStack API doesn't allow multiple countries in one page fetch, so we loop over countries
        for country in countries:
            print(f"  Country: {country}")
            data = fetch_articles(query, country)
            if data:
                articles = data.get('data', [])
                print(f"    Articles found for {country}: {len(articles)}")
                if articles:
                    all_articles.extend(articles)
                else:
                    print(f"    No articles found for {country}.")
        
        if all_articles:
            # Remove duplicates by URL (optional)
            seen_urls = set()
            unique_articles = []
            for art in all_articles:
                if art['url'] not in seen_urls:
                    unique_articles.append(art)
                    seen_urls.add(art['url'])
            
            # Save to CSV
            safe_query = query.replace(" ", "_")
            filename = f"media_stack_{safe_query}_headlines.csv"
            save_articles_to_csv(filename, unique_articles)
        else:
            print(f"No articles found for query '{query}' from the selected countries.")

if __name__ == "__main__":
    main()

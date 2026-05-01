import requests
from datetime import datetime
import os
import csv

API_KEY = "f7161d5be3e808239883bfc2973beb0f"  # Your GNews API key
BASE_URL = "https://gnews.io/api/v4/search"

# Queries to search
queries = ["pahalgam attack", "operation sindoor"]

# Countries (2-letter ISO codes) per GNews docs
countries = ['in', 'us', 'gb', 'pk', 'tr', 'au', 'cn', 'bd', 'lk']

# Date range
from_date = "2025-04-22"
to_date = datetime.today().strftime("%Y-%m-%d")

# Output directory
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

def fetch_articles(query, country, page=1, max_results=100):
    params = {
        "q": query,                # Search query
        "lang": "en",              # Language filter
        "country": country,        # Country filter (ISO 2-letter code)
        "from": from_date,         # Start date (inclusive)
        "to": to_date,             # End date (inclusive)
        "max": max_results,        # Max number of articles per request
        "page": page,              # Pagination (page number)
        "token": API_KEY,          # API token
    }
    try:
        response = requests.get(BASE_URL, params=params)
        print(f"API Response for country {country}: {response.status_code}")
        print("Raw Response:", response.text)  # To see the actual API response
        
        response.raise_for_status()  # Will raise an HTTPError for 4xx/5xx responses
        
        # If status code is 200, return parsed JSON
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error for country {country}: {errh}")
    except requests.exceptions.RequestException as err:
        print(f"Error fetching data for country {country}: {err}")
    return None

def save_articles_to_csv(filename, articles):
    csv_path = os.path.join(output_dir, filename)
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['source_name', 'author', 'title', 'description', 'url', 'publishedAt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow({
                'source_name': article.get('source', {}).get('name', ''),
                'author': article.get('author', ''),
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', '')
            })
    print(f"Saved {len(articles)} articles to {csv_path}")

def main():
    for query in queries:
        print(f"\nFetching articles for: '{query}'")
        all_articles = []
        
        for country in countries:
            print(f"  Country: {country}")
            data = fetch_articles(query, country)
            if data:
                articles = data.get('articles', [])
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
            filename = f"gnews_{safe_query}_headlines.csv"
            save_articles_to_csv(filename, unique_articles)
        else:
            print(f"No articles found for query '{query}' from the selected countries.")

if __name__ == "__main__":
    main()

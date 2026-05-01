import tweepy
import csv
import os
import time
from datetime import datetime, timezone

# Your Twitter API credentials (Bearer Token for Twitter API v2)
BEARER_TOKEN = r'AAAAAAAAAAAAAAAAAAAAAGtd2AEAAAAAnkxqQeGAMccKHFyYMiBHUd5JLOM%3D5UhYyWIOs9uZncEySFsP6Z717GdqqS71t700DVy8xHdcnP4LxU'

# Tweepy client setup for Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=False)

# Parameters
HANDLES = ['ANI', 'PTI_News', 'economictimes', 'firstpost', 'the_hindu', 'timesofindia', 'SkyNews']
START_DATE = datetime(2025, 4, 22, tzinfo=timezone.utc)
END_DATE = datetime(2025, 5, 22, tzinfo=timezone.utc)
MAX_TWEETS_PER_USER = 1000  # max tweets per handle

# Output CSV file
OUTPUT_FILE = 'outputs/tweepy-data-all-tweets.csv'
os.makedirs('outputs', exist_ok=True)

FIELDNAMES = ['author', 'likes', 'comments', 'tweet_message', 'country', 'timestamp']

def write_header_if_not_exists(filename, fieldnames):
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

def append_tweets_to_csv(tweets, filename, fieldnames):
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for tweet in tweets:
            writer.writerow(tweet)

def get_user_id(username):
    try:
        user = client.get_user(username=username)
        if user and user.data:
            return user.data.id
        else:
            print(f"User {username} not found!")
            return None
    except Exception as e:
        print(f"Error fetching user ID for {username}: {e}")
        return None

def fetch_user_tweets(user_id, username):
    tweets_collected = 0
    pagination_token = None

    while tweets_collected < MAX_TWEETS_PER_USER:
        max_results = min(100, MAX_TWEETS_PER_USER - tweets_collected)
        try:
            response = client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                pagination_token=pagination_token,
                tweet_fields=['created_at', 'public_metrics', 'text'],
                expansions=['author_id'],
                user_fields=['location', 'username'],
                exclude=['retweets'],  # exclude retweets
            )
        except Exception as e:
            print(f"Error fetching tweets for user {username}: {e}")
            print("Waiting 15 minutes before retrying...")
            time.sleep(900)
            continue

        if not response.data:
            print(f"No more tweets found for user {username}.")
            break

        user_info = None
        if response.includes and 'users' in response.includes:
            user_info = response.includes['users'][0]

        tweets_data = []
        for tweet in response.data:
            created_at = tweet.created_at
            if created_at is None:
                continue
            if created_at < START_DATE or created_at > END_DATE:
                continue

            tweets_data.append({
                'author': username,
                'likes': tweet.public_metrics.get('like_count', 0),
                'comments': tweet.public_metrics.get('reply_count', 0),
                'tweet_message': tweet.text,
                'country': user_info.location if user_info else '',
                'timestamp': created_at.isoformat()
            })

        if tweets_data:
            append_tweets_to_csv(tweets_data, OUTPUT_FILE, FIELDNAMES)
            print(f"Appended {len(tweets_data)} tweets for user {username}")

        tweets_collected += len(response.data)

        if 'next_token' in response.meta:
            pagination_token = response.meta['next_token']
        else:
            break

        print("Waiting 15 minutes due to rate limit...")
        time.sleep(900)

    print(f"Finished fetching tweets for user {username}. Total tweets scanned: {tweets_collected}")

def main():
    write_header_if_not_exists(OUTPUT_FILE, FIELDNAMES)

    for username in HANDLES:
        print(f"Starting data fetch for: {username}")
        user_id = get_user_id(username)
        if not user_id:
            print(f"Skipping user {username} due to missing user ID.")
            continue
        fetch_user_tweets(user_id, username)
        print(f"Completed data fetch for: {username}\n{'-'*50}")

if __name__ == '__main__':
    main()

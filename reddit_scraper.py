#!/usr/bin/env python3
"""
Reddit scraper for r/ausjdocs - Extract pharmacy-related posts
"""

import requests  # For sending HTTP requests
import json  # For working with JSON data
import time  # For adding time delays
from datetime import datetime  # To handle date and time
import csv  # For saving data in CSV format
import logging  # For logging messages (info, warnings, errors)

# Constants for repeated values
BASE_URL = 'https://old.reddit.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

class RedditScraper:
    def __init__(self):
        # Initialize headers and base URL for requests
        self.headers = {
            'User-Agent': USER_AGENT
        }
    
    def fetch_with_retry(self, url, params, retries=3):
        """Send a GET request with retries in case of network failures."""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()  # If status is not 200, raise an exception
                return response.json()  # Parse and return JSON data
            except requests.exceptions.RequestException as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)  # Wait before retrying
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON: {e}")
                break  # Stop retrying if the response can't be parsed
        return None  # Return None if all retries fail

    def search_subreddit(self, subreddit, query, limit=100):
        """Search a subreddit for posts containing the specified keywords."""
        posts = []  # List to hold the found posts
        after = None  # Used for pagination (getting the next set of results)
        
        logging.info(f"Searching r/{subreddit} for '{query}'...")
        
        while True:
            url = f"{BASE_URL}/r/{subreddit}/search.json"
            params = {
                'q': query,  # The search query
                'restrict_sr': 'on',  # Restrict to subreddit
                'sort': 'new',  # Sort results by newest
                'limit': 100,  # Limit the results per request
                't': 'all'  # Search across all time
            }
            if after:
                params['after'] = after  # Add the next page token if available
            
            # Fetch the data with retries
            data = self.fetch_with_retry(url, params)
            if not data:
                break  # Stop if we couldn't fetch the data
            
            children = data['data']['children']
            if not children:  # No more posts found
                logging.info("No more posts found")
                break
            
            # Extract post details and append to posts list
            for child in children:
                post_data = child['data']
                post = self.extract_post_data(post_data)
                posts.append(post)
            
            logging.info(f"Collected {len(posts)} posts so far...")
            after = data['data'].get('after')  # Get the token for the next page
            if not after:  # If no more pages, stop
                logging.info("Reached end of results")
                break
            
            time.sleep(2)  # Be polite and wait before sending another request
        
        return posts[:limit]  # Return the first 'limit' posts

    def extract_post_data(self, post_data):
        """Extract relevant data from a post's details."""
        return {
            'title': post_data.get('title', ''),
            'author': post_data.get('author', ''),
            'score': post_data.get('score', 0),
            'num_comments': post_data.get('num_comments', 0),
            'created_utc': post_data.get('created_utc', 0),
            'created_date': datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S'),
            'selftext': post_data.get('selftext', ''),
            'url': f"{BASE_URL}{post_data.get('permalink', '')}",
            'id': post_data.get('id', ''),
            'link_flair_text': post_data.get('link_flair_text', ''),
        }

    def get_post_comments(self, post_url):
        """Get comments from a specific post."""
        url = f"{post_url}.json"
        data = self.fetch_with_retry(url, {})
        if not data:
            return []  # Return empty if no data
        
        comments = []
        if len(data) > 1:  # Check if there are comments
            comment_data = data[1]['data']['children']
            comments = self._extract_comments(comment_data)  # Extract comment details
        
        time.sleep(2)  # Politeness delay
        return comments

    def _extract_comments(self, comment_data):
        """Extract comments and their replies."""
        comments = []
        stack = [(comment_data, 0)]  # Use a stack to handle comments and their replies
        
        while stack:
            data, depth = stack.pop()
            for item in data:
                if item['kind'] == 't1':  # Check if it's a comment (not a post)
                    comment = item['data']
                    comments.append({
                        'author': comment.get('author', ''),
                        'body': comment.get('body', ''),
                        'score': comment.get('score', 0),
                        'created_utc': comment.get('created_utc', 0),
                        'depth': depth  # Track the depth of replies
                    })
                    
                    # Check for replies
                    if 'replies' in comment and comment['replies']:
                        if isinstance(comment['replies'], dict):
                            stack.append((comment['replies']['data']['children'], depth + 1))
        
        return comments

    def save_to_json(self, data, filename):
        """Save the data to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)  # Write data as JSON
        logging.info(f"Saved to {filename}")

    def save_to_csv(self, posts, filename):
        """Save the posts to a CSV file."""
        if not posts:  # If no posts to save
            logging.warning("No posts to save")
            return
        
        keys = posts[0].keys()  # Use the keys from the first post as headers
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()  # Write header row
            writer.writerows(posts)  # Write the posts
        logging.info(f"Saved to {filename}")


def main():
    scraper = RedditScraper()  # Create an instance of RedditScraper
    
    # Search terms related to pharmacy
    search_terms = [
        'pharmacist',
        'pharmacy',
        'pharmacists',
        'clinical pharmacist',
        'ward pharmacist'
    ]
    
    all_posts = []  # List to store all unique posts
    seen_ids = set()  # Set to keep track of already seen post IDs
    
    for term in search_terms:  # Loop through each search term
        logging.info(f"\n{'='*60}")
        logging.info(f"Searching for: {term}")
        logging.info(f"{'='*60}")
        
        posts = scraper.search_subreddit('ausjdocs', term, limit=200)  # Search the subreddit
        
        # Remove duplicates by checking post IDs
        for post in posts:
            if post['id'] not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post['id'])
        
        time.sleep(3)  # Extra delay between searches to be polite
    
    logging.info(f"\n{'='*60}")
    logging.info(f"Total unique posts found: {len(all_posts)}")
    logging.info(f"{'='*60}")
    
    # Save the results to JSON and CSV
    output_dir = '.'
    scraper.save_to_json(all_posts, f'{output_dir}/ausjdocs_pharmacy_posts.json')
    scraper.save_to_csv(all_posts, f'{output_dir}/ausjdocs_pharmacy_posts.csv')
    
    # Optional: Fetch comments for top posts
    logging.info("\nWould you like to fetch comments? (Uncomment below if yes)")
    # for i, post in enumerate(all_posts[:10]):  # Get comments for top 10 posts
    #     logging.info(f"Fetching comments for post {i+1}/10...")
    #     comments = scraper.get_post_comments(post['url'])
    #     post['comments'] = comments
    
    logging.info("\nDone! Check the outputs folder for your data.")


if __name__ == "__main__":
    main()  # Run the main function

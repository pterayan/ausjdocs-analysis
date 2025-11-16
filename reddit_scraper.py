#!/usr/bin/env python3
"""
Reddit scraper for r/ausjdocs - Extract pharmacy-related posts
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import csv

class RedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = 'https://old.reddit.com'
        
    def search_subreddit(self, subreddit, query, limit=100):
        """Search a subreddit for specific keywords"""
        posts = []
        after = None
        
        print(f"Searching r/{subreddit} for '{query}'...")
        
        while len(posts) < limit:
            # Build URL
            url = f"{self.base_url}/r/{subreddit}/search.json"
            params = {
                'q': query,
                'restrict_sr': 'on',  # Restrict to this subreddit
                'sort': 'new',  # Sort by newest first
                'limit': 100,  # Max per request
                't': 'all'  # All time
            }
            
            if after:
                params['after'] = after
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract posts
                children = data['data']['children']
                
                if not children:
                    print("No more posts found")
                    break
                
                for child in children:
                    post_data = child['data']
                    
                    post = {
                        'title': post_data.get('title', ''),
                        'author': post_data.get('author', ''),
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc', 0),
                        'created_date': datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        'selftext': post_data.get('selftext', ''),
                        'url': f"{self.base_url}{post_data.get('permalink', '')}",
                        'id': post_data.get('id', ''),
                        'link_flair_text': post_data.get('link_flair_text', ''),
                    }
                    posts.append(post)
                
                print(f"Collected {len(posts)} posts so far...")
                
                # Get next page token
                after = data['data'].get('after')
                if not after:
                    print("Reached end of results")
                    break
                
                # Be polite - rate limit
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                break
        
        return posts[:limit]
    
    def get_post_comments(self, post_url):
        """Get comments from a specific post"""
        try:
            url = f"{post_url}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            comments = []
            if len(data) > 1:
                comment_data = data[1]['data']['children']
                comments = self._extract_comments(comment_data)
            
            time.sleep(2)  # Rate limiting
            return comments
            
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return []
    
    def _extract_comments(self, comment_data, depth=0):
        """Recursively extract comments and replies"""
        comments = []
        
        for item in comment_data:
            if item['kind'] == 't1':  # Comment
                comment = item['data']
                comments.append({
                    'author': comment.get('author', ''),
                    'body': comment.get('body', ''),
                    'score': comment.get('score', 0),
                    'created_utc': comment.get('created_utc', 0),
                    'depth': depth
                })
                
                # Get replies
                if 'replies' in comment and comment['replies']:
                    if isinstance(comment['replies'], dict):
                        replies = comment['replies']['data']['children']
                        comments.extend(self._extract_comments(replies, depth + 1))
        
        return comments
    
    def save_to_json(self, data, filename):
        """Save data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved to {filename}")
    
    def save_to_csv(self, posts, filename):
        """Save posts to CSV file"""
        if not posts:
            print("No posts to save")
            return
        
        keys = posts[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(posts)
        print(f"Saved to {filename}")


def main():
    scraper = RedditScraper()
    
    # Search terms related to pharmacy
    search_terms = [
        'pharmacist',
        'pharmacy',
        'pharmacists',
        'clinical pharmacist',
        'ward pharmacist'
    ]
    
    all_posts = []
    seen_ids = set()
    
    for term in search_terms:
        print(f"\n{'='*60}")
        print(f"Searching for: {term}")
        print(f"{'='*60}")
        
        posts = scraper.search_subreddit('ausjdocs', term, limit=200)
        
        # Remove duplicates
        for post in posts:
            if post['id'] not in seen_ids:
                all_posts.append(post)
                seen_ids.add(post['id'])
        
        time.sleep(3)  # Be extra polite between searches
    
    print(f"\n{'='*60}")
    print(f"Total unique posts found: {len(all_posts)}")
    print(f"{'='*60}")
    
    # Save results
    output_dir = '.'
    
    scraper.save_to_json(all_posts, f'{output_dir}/ausjdocs_pharmacy_posts.json')
    scraper.save_to_csv(all_posts, f'{output_dir}/ausjdocs_pharmacy_posts.csv')
    
    # Optional: Get comments for top posts
    print("\nWould you like to fetch comments? (Uncomment below if yes)")
    # for i, post in enumerate(all_posts[:10]):  # Get comments for top 10 posts
    #     print(f"Fetching comments for post {i+1}/10...")
    #     comments = scraper.get_post_comments(post['url'])
    #     post['comments'] = comments
    
    print("\nDone! Check the outputs folder for your data.")


if __name__ == "__main__":
    main()

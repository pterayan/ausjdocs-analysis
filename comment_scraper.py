#!/usr/bin/env python3
"""
Scrape comments from specific r/ausjdocs posts about hospital pharmacy collaboration
"""

import requests
import json
import time

class CommentScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = 'https://old.reddit.com'
    
    def get_post_comments(self, post_id):
        """Fetch all comments from a specific post"""
        url = f"{self.base_url}/r/ausjdocs/comments/{post_id}.json"
        
        try:
            print(f"Fetching comments for post {post_id}...")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if len(data) < 2:
                print("  ⚠️ No comments found")
                return []
            
            # Extract post info
            post_data = data[0]['data']['children'][0]['data']
            post_info = {
                'title': post_data['title'],
                'selftext': post_data.get('selftext', ''),
                'score': post_data['score'],
                'num_comments': post_data['num_comments']
            }
            
            # Extract comments
            comments = self._extract_comments(data[1]['data']['children'])
            
            print(f"  ✅ Found {len(comments)} comments")
            
            time.sleep(2)  # Be polite
            
            return {
                'post_id': post_id,
                'post_info': post_info,
                'comments': comments
            }
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def _extract_comments(self, comment_data, depth=0):
        """Recursively extract comments and replies"""
        comments = []
        
        for item in comment_data:
            if item['kind'] == 't1':  # Comment type
                comment = item['data']
                
                # Skip deleted/removed comments
                if comment.get('author') in ['[deleted]', 'AutoModerator']:
                    continue
                
                comment_obj = {
                    'author': comment.get('author', ''),
                    'body': comment.get('body', ''),
                    'score': comment.get('score', 0),
                    'created_utc': comment.get('created_utc', 0),
                    'depth': depth,
                    'is_submitter': comment.get('is_submitter', False),  # OP's reply
                    'replies': []
                }
                
                # Get replies recursively
                if 'replies' in comment and comment['replies']:
                    if isinstance(comment['replies'], dict):
                        replies_data = comment['replies']['data']['children']
                        comment_obj['replies'] = self._extract_comments(replies_data, depth + 1)
                
                comments.append(comment_obj)
        
        return comments


def main():
    """Scrape comments from key hospital pharmacy posts"""
    
    # Key post IDs we identified
    key_posts = {
        '1owkkre': 'Hospital pharmacist - seeking feedback',
        '1fvwiyt': 'What do you guys think of us?',
        '1fvvt2c': 'Excellent pharmacists mention',
        '1oxmpn5': 'GPs and pharmacist calls'
    }
    
    scraper = CommentScraper()
    all_data = {}
    
    print("="*70)
    print("SCRAPING COMMENTS FROM KEY COLLABORATIVE POSTS")
    print("="*70)
    print()
    
    for post_id, description in key_posts.items():
        print(f"\n{description}")
        print("-" * 70)
        
        result = scraper.get_post_comments(post_id)
        if result:
            all_data[post_id] = result
        
        time.sleep(3)  # Extra polite between posts
    
    # Save to file
    output_file = 'hospital_pharmacy_comments.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print(f"✅ COMPLETE - Saved to {output_file}")
    print("="*70)
    
    # Summary
    total_comments = sum(len(data['comments']) for data in all_data.values())
    print(f"\n📊 SUMMARY:")
    print(f"   Posts scraped: {len(all_data)}")
    print(f"   Total comments: {total_comments}")
    print()
    
    for post_id, data in all_data.items():
        print(f"   {data['post_info']['title'][:50]}...")
        print(f"      Comments: {len(data['comments'])}")
        print()


if __name__ == "__main__":
    main()

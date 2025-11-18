#!/usr/bin/env python3
"""
Scrape comments from specific r/ausjdocs posts about hospital pharmacy collaboration
"""

import requests  # For sending HTTP requests to Reddit
import json  # For working with JSON data
import time  # For adding time delays (to be polite to Reddit)

class CommentScraper:
    def __init__(self):
        # Initialize headers for the requests with a User-Agent string (to simulate a browser request)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = 'https://old.reddit.com'  # Reddit's old site URL (more stable for scraping)
    
    def get_post_comments(self, post_id):
        """Fetch all comments from a specific post"""
        url = f"{self.base_url}/r/ausjdocs/comments/{post_id}.json"  # URL for the comments of a specific post
        
        try:
            print(f"Fetching comments for post {post_id}...")
            response = requests.get(url, headers=self.headers)  # Make a GET request to fetch data
            response.raise_for_status()  # Check if the request was successful (status code 200)
            data = response.json()  # Parse the response data as JSON
            
            if len(data) < 2:  # If there's no comment data
                print("  ⚠️ No comments found")
                return []  # Return empty list if no comments are found
            
            # Extract the post's information (title, text, score, and number of comments)
            post_data = data[0]['data']['children'][0]['data']
            post_info = {
                'title': post_data['title'],
                'selftext': post_data.get('selftext', ''),  # Get selftext if available, else empty string
                'score': post_data['score'],
                'num_comments': post_data['num_comments']
            }
            
            # Extract the comments from the data
            comments = self._extract_comments(data[1]['data']['children'])
            
            print(f"  ✅ Found {len(comments)} comments")  # Print how many comments were found
            
            time.sleep(2)  # Be polite and wait for 2 seconds before making the next request
            
            return {
                'post_id': post_id,  # Include the post ID in the returned data
                'post_info': post_info,  # Include post information
                'comments': comments  # Include the list of comments
            }
            
        except Exception as e:
            print(f"  ❌ Error: {e}")  # Print any errors that occur
            return None  # Return None if there's an error

    def _extract_comments(self, comment_data, depth=0):
        """Recursively extract comments and replies"""
        comments = []  # Initialize an empty list to store extracted comments
        
        for item in comment_data:
            if item['kind'] == 't1':  # 't1' indicates a comment (not a post)
                comment = item['data']
                
                # Skip deleted or automatically moderated comments
                if comment.get('author') in ['[deleted]', 'AutoModerator']:
                    continue
                
                # Create a comment object with relevant fields
                comment_obj = {
                    'author': comment.get('author', ''),  # Get the author's name
                    'body': comment.get('body', ''),  # Get the comment body
                    'score': comment.get('score', 0),  # Get the score (upvotes)
                    'created_utc': comment.get('created_utc', 0),  # Get the creation time in UTC
                    'depth': depth,  # Keep track of the comment depth (to handle replies)
                    'is_submitter': comment.get('is_submitter', False),  # Check if this is the OP's reply
                    'replies': []  # Initialize an empty list for replies (nested comments)
                }
                
                # If there are replies to the comment, recursively extract them
                if 'replies' in comment and comment['replies']:
                    if isinstance(comment['replies'], dict):  # Ensure replies are in a dict format
                        replies_data = comment['replies']['data']['children']  # Extract replies
                        comment_obj['replies'] = self._extract_comments(replies_data, depth + 1)  # Recursively get replies
                
                # Append the comment object to the list of comments
                comments.append(comment_obj)
        
        return comments  # Return the list of comments

def main():
    """Scrape comments from key hospital pharmacy posts"""
    
    # Key post IDs we identified based on specific topics of interest
    key_posts = {
        '1owkkre': 'Hospital pharmacist - seeking feedback',  # Post ID and title
        '1fvwiyt': 'What do you guys think of us?',  # Another post ID and title
        '1fvvt2c': 'Excellent pharmacists mention',  # Another post ID and title
        '1oxmpn5': 'GPs and pharmacist calls'  # Another post ID and title
    }
    
    scraper = CommentScraper()  # Create an instance of the CommentScraper class
    all_data = {}  # Dictionary to store all the fetched data
    
    print("="*70)
    print("SCRAPING COMMENTS FROM KEY COLLABORATIVE POSTS")  # Header for the process
    print("="*70)
    print()
    
    # Loop through each post ID and description in the 'key_posts' dictionary
    for post_id, description in key_posts.items():
        print(f"\n{description}")  # Print the description of the post being processed
        print("-" * 70)
        
        # Fetch comments for the current post
        result = scraper.get_post_comments(post_id)
        if result:
            all_data[post_id] = result  # Store the result if successful
        
        time.sleep(3)  # Extra polite delay between each post request
    
    # Save the data to a JSON file
    output_file = 'hospital_pharmacy_comments.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)  # Write the data as a formatted JSON file
    
    print("\n" + "="*70)
    print(f"✅ COMPLETE - Saved to {output_file}")  # Confirmation message
    print("="*70)
    
    # Summary of the scraping process
    total_comments = sum(len(data['comments']) for data in all_data.values())  # Total number of comments scraped
    print(f"\n📊 SUMMARY:")
    print(f"   Posts scraped: {len(all_data)}")  # Total number of posts scraped
    print(f"   Total comments: {total_comments}")  # Total number of comments
    
    # Print a brief summary of each post and its comments
    for post_id, data in all_data.items():
        print(f"   {data['post_info']['title'][:50]}...")  # Display the post title (first 50 characters)
        print(f"      Comments: {len(data['comments'])}")  # Number of comments for each post
        print()

if __name__ == "__main__":
    main()  # Run the main function to start scraping

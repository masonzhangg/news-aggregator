import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html
from supabase import create_client, Client
from dotenv import load_dotenv
from .aisummarizer import (
    normal_news_list,
    sports_summary,
    tech_summary,
    health_summary,
    politics_summary
)

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scrape_and_insert_news(query, category, num_articles=10):
    # Scrape articles
    articles = normal_news_list(query, num_articles)
    
    # Loop through each article and summarize it based on category
    for article in articles:
        title = article['title']
        content = article['content']
        article_url = article['link']

        # Summarize based on category
        if category == "sports":
            summary = sports_summary(content)
        elif category == "technology":
            summary = tech_summary(content)
        elif category == "health":
            summary = health_summary(content)
        elif category == "politics":
            summary = politics_summary(content)
        else:
            summary = "Category not supported for summarization."

        # Insert the article and its summary into Supabase
        insert_article_into_supabase(category, title, content, article_url, summary)

def insert_article_into_supabase(category, title, content, url, summary):
    """Insert article data along with its summary into Supabase"""
    try:
        data = {
            "title": title,
            "content": content,
            "url": url,
            "summary": summary
        }
        response = supabase.table(f"{category}_articles").insert(data).execute()
        if response.status_code == 200:
            print(f"Successfully inserted article: {title}")
        else:
            print(f"Failed to insert article: {title}")
    except Exception as e:
        print(f"Error inserting article into Supabase: {e}")

# Main function to scrape and insert news
def main():
    categories = ['sports', 'technology', 'health', 'politics']
    for category in categories:
        scrape_and_insert_news(query=category, category=category)
        print(f"Finished processing {category} news.")

if __name__ == "__main__":
    main()

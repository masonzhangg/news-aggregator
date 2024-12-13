import os
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from aisummarizer import sports_summary, tech_summary, normal_news_list, health_summary, politics_summary, summarize_with_retrieval_and_rag
from supabase import create_client, Client
from webscrape import scrape_and_insert_news

app = FastAPI()

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CompanyRequest(BaseModel):
    company_name: str

# Function to insert news into Supabase (both title and content)
def insert_article(supabase_client: Client, table_name: str, title: str, content: str, news_url: str):
    current_date = datetime.now().date()
    data = {
        "date": str(current_date),
        "title": title,
        "content": content,
        "news_url": news_url
    }
    try:
        supabase_client.table(table_name).insert(data).execute()
    except Exception as e:
        print(f"Error inserting article into {table_name}: {e}")

# Function to insert summary into Supabase
def insert_summary(supabase_client: Client, table_name: str, summary: str, news_url: str, news_title: str):
    current_date = datetime.now().date()
    data = {
        "date": str(current_date),
        "summary": summary,
        "news_title": news_title,
        "news_url": news_url
    }
    try:
        supabase_client.table(table_name).insert(data).execute()
    except Exception as e:
        print(f"Error inserting summary into {table_name}: {e}")


# Function to summarize and upload sports news
def summarize_and_upload_news(supabase_client: Client, category: str, summary_function):
    try:
        # Get list of articles
        news_list = normal_news_list(category, 10)
        for news in news_list:
            # Save article content and title to Supabase
            insert_article(supabase_client, f"{category}_articles", news['title'], news['content'], news['link'])
            
            # Summarize the content
            summary = summary_function(news['content'])
            if 'not relevant' not in summary.lower():
                # Save summary into Supabase
                insert_summary(supabase_client, f"{category}_summary", summary, news['link'], news['title'])
    except Exception as e:
        print(f"Error summarizing {category} news: {e}")

        print(f"Error summarizing {category} news: {e}")

# Main endpoint to upload all summaries (sports, tech, health, politics)

@app.post("/summarize/")
async def summarize_news(query: str, category: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(summarize_with_retrieval_and_rag, supabase, query, category)
    return {"message": "Summarization started"}


@app.post("/upload_all/")
async def upload_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_and_insert_news, 'sports', 'sports')
    background_tasks.add_task(scrape_and_insert_news, 'technology', 'technology')
    background_tasks.add_task(scrape_and_insert_news, 'politics', 'politics')
    background_tasks.add_task(scrape_and_insert_news, 'health', 'health')
    return {"message": "Uploading all news summaries"}

# Run the server only if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
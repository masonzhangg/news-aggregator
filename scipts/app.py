import os
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from aisummarizer import sports_summary, tech_summary, normal_news_list, health_summary, politics_summary
from supabase import create_client, Client

app = FastAPI()

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CompanyRequest(BaseModel):
    company_name: str

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
def summarize_and_upload_sports_news(supabase_client: Client):
    try:
        news_list = normal_news_list('sports', 10)
        for news in news_list:
            summary = sports_summary(news['content'])
            if 'not relevant' not in summary.lower():
                insert_summary(supabase_client, "sports_summary", summary, news['link'], news['title'])
    except Exception as e:
        print(f"Error summarizing sports news: {e}")

# Function to summarize and upload tech news
def summarize_and_upload_tech_news(supabase_client: Client):
    try:
        news_list = normal_news_list('technology', 10)
        for news in news_list:
            summary = tech_summary(news['content'])
            if 'not relevant' not in summary.lower():
                insert_summary(supabase_client, "tech_summary", summary, news['link'], news['title'])
    except Exception as e:
        print(f"Error summarizing tech news: {e}")

# Function to summarize and upload health news
def summarize_and_upload_health_news(supabase_client: Client):
    try:
        news_list = normal_news_list('health', 10)
        for news in news_list:
            summary = health_summary(news['content'])
            if 'not relevant' not in summary.lower():
                insert_summary(supabase_client, "health_summary", summary, news['link'], news['title'])
    except Exception as e:
        print(f"Error summarizing health news: {e}")

# Function to summarize and upload politics news
def summarize_and_upload_politics_news(supabase_client: Client):
    try:
        news_list = normal_news_list('politics', 10)
        for news in news_list:
            summary = politics_summary(news['content'])
            if 'not relevant' not in summary.lower():
                insert_summary(supabase_client, "politics_summary", summary, news['link'], news['title'])
    except Exception as e:
        print(f"Error summarizing politics news: {e}")

# Main endpoint to upload all summaries (sports, tech, health, politics)
@app.post("/upload_all/")
async def upload_all(background_tasks: BackgroundTasks):
    background_tasks.add_task(summarize_and_upload_sports_news, supabase)
    background_tasks.add_task(summarize_and_upload_tech_news, supabase)
    background_tasks.add_task(summarize_and_upload_health_news, supabase)
    background_tasks.add_task(summarize_and_upload_politics_news, supabase)
    return {"message": "Uploading all news summaries"}

# Run the server only if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

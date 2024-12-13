import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatVertexAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from supabase import create_client, Client

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def getNewsData(query,num):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    response = requests.get(
        f"https://www.google.com/search?q={query}&gl=us&tbm=nws&num={str(num)}", headers=headers
    )
    soup = BeautifulSoup(response.content, "html.parser")
    news_results = []

    for el in soup.select("div.SoaBEf"):
        news_results.append(
            {
                "link": el.find("a")["href"],
                "title": el.select_one("div.MBeuO").get_text(),
                "snippet": el.select_one(".GI74Re").get_text(),
                "date": el.select_one(".LfVVr").get_text(),
                "source": el.select_one(".NUnG9d span").get_text()
            }
        )

    return news_results

def get_news_data_from_url(url):
    # can be used for all three news categories
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Adjust scraping logic for Yahoo Finance articles
    articles = soup.find_all('article')
    if not articles:
        articles = soup.find_all('div', class_=lambda x: x and 'article' in x.split())
    if not articles:
        articles = soup.find_all('div', class_=lambda x: x and 'news' in x.split())
    if not articles:
        articles = [div for div in soup.find_all('div') if div.find(['h1', 'h2', 'h3'])]

    news_result = None  # Initialize news_result

    for el in articles:
        title_element = el.find('h1') or el.find('h2') or el.find('h3')
        link_element = el.find('a', href=True)
        date_element = el.find('time')
        source_element = el.find('span', class_='source') or el.find('span', class_='author')

        article_text = ' '.join(p.get_text(strip=True) for p in el.find_all('p'))
        link_url = urljoin(url, link_element['href']) if link_element and link_element['href'] else ''
        title = html.unescape(title_element.get_text(strip=True) if title_element else '')
        article_text = html.unescape(article_text)

        news_result = {
            "link": link_url,
            "title": title,
            "article_text": article_text,
            "date": html.unescape(date_element.get_text(strip=True) if date_element else ''),
            "source": html.unescape(source_element.get_text(strip=True) if source_element else '')
        }
        break  # Only process the first article

    if news_result is None:
        # If no article is found, return a default value or raise an exception
        return {"link": "", "title": "", "article_text": "", "date": "", "source": ""}
        # Or raise an exception: raise ValueError("No article found on the page")

    return news_result

def normal_news_list(query, num):
    search_results = getNewsData(query, num)

    news_list = []
    for result in search_results:
        url = result['link']
        title = result['title']

        # get content from each article
        article_data = get_news_data_from_url(url)

        # only add to the list if the article content is not empty
        if article_data['article_text'].strip():
            news_item = {
                'link': url,
                'title': title,
                'content': article_data['article_text']
            }
            news_list.append(news_item)

    return news_list
 
#SPORTS SUMMARY
def sports_summary(content: str):
    llm = ChatVertexAI(api_key=GEMINI_API_KEY,
                     temperature=0,
                     model="gemini-1.5-flash")

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"],
                                                   chunk_size=10000,
                                                   chunk_overlap=500)

    docs = text_splitter.create_documents([content])

    map_prompt = """
    As a sports analyst, please summarize the following sports news content and extract key highlights and events:

    "{text}"

    YOU DO NOT MAKE UP CONTENTS!

    Please include the following in your summary ONLY if mentioned:
    1. Final scores and results of important matches or games
    2. Key events and turning points in the games
    3. Notable performances by players or teams
    4. Important quotes from players, coaches, or analysts
    5. Implications for standings, rankings, or future games
    6. Any relevant injuries or updates affecting players or teams

    Please ensure all important numbers, statistics, and quotes are retained.
    Your summary should be CONCISE and you do not make up any content.
    If the content is not related to sports news, please respond with *NOT RELEVANT*.

    Summary:
    """

    map_prompt_template = PromptTemplate(template=map_prompt,
                                         input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs)
    return output


#TECH SUMMARY
def tech_summary(content: str):
    llm = ChatVertexAI(api_key=GEMINI_API_KEY,
                     temperature=0,
                     model="gemini-1.5-flash")

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"],
                                                   chunk_size=10000,
                                                   chunk_overlap=500)

    docs = text_splitter.create_documents([content])

    map_prompt = """
    As a technology analyst, please summarize the following tech news content and extract key highlights and events:

    "{text}"

    YOU DO NOT MAKE UP CONTENTS!

    Please include the following in your summary ONLY if mentioned:
    1. Major product launches and announcements
    2. Innovations and new technologies introduced
    3. Key company news (e.g., earnings, mergers, partnerships)
    4. Important quotes from executives, experts, or analysts
    5. Significant impacts on the market or industry

    Please ensure all important numbers, statistics, and quotes are retained.
    If the content is not related to technology news, please respond with *NOT RELEVANT*.

    Summary:
    """

    map_prompt_template = PromptTemplate(template=map_prompt,
                                         input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs)
    return output

# HEALTH SUMMARY
def health_summary(content: str):
    llm = ChatVertexAI(api_key=GEMINI_API_KEY,
                     temperature=0,
                     model="gemini-1.5-flash")

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"],
                                                   chunk_size=10000,
                                                   chunk_overlap=500)

    docs = text_splitter.create_documents([content])

    map_prompt = """
    As a health analyst, please summarize the following health news content and extract key highlights and events:

    "{text}"

    YOU DO NOT MAKE UP CONTENTS!

    Please include the following in your summary ONLY if mentioned:
    1. Medical Breakthroughs
    2. Innovations and new technologies introduced
    3. Key company news (e.g., earnings, mergers, partnerships)
    4. Important quotes from experts or analysts
    5. Significant impacts on the market or industry
    6. Any relevant updates or developments
    7. Any relevant medical research or advancements
    8. Any relevant medical treatments or procedures

    Please ensure all important numbers, statistics, and quotes are retained.
    If the content is not related to health news, please respond with *NOT RELEVANT*.

    Summary:
    """

    map_prompt_template = PromptTemplate(template=map_prompt,
                                         input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs)
    return output

# POLITICS SUMMARY
def politics_summary(content: str):
    llm = ChatVertexAI(api_key=GEMINI_API_KEY,
                     temperature=0,
                     model="gemini-1.5-flash")

    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"],
                                                   chunk_size=10000,
                                                   chunk_overlap=500)

    docs = text_splitter.create_documents([content])

    map_prompt = """
    As a politics analyst, please summarize the following politics news content and extract key highlights and events:

    "{text}"

    YOU DO NOT MAKE UP CONTENTS!

    Please include the following in your summary ONLY if mentioned:
    1. Major political events and developments
    2. Key policy changes or decisions
    3. Important quotes from politicians or experts
    4. Significant impacts on the political landscape
    5. Any relevant updates or developments
    6. Any relevant political research or analysis
    7. Any relevant political movements or trends
    8. Any relevant political controversies or debates

    Please ensure all important numbers, statistics, and quotes are retained.
    If the content is not related to political news, please respond with *NOT RELEVANT*.

    Summary:
    """

    map_prompt_template = PromptTemplate(template=map_prompt,
                                         input_variables=["text"])

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )

    output = summary_chain.run(input_documents=docs)
    return output

# Function to retrieve articles from Supabase based on category
def retrieve_articles_from_supabase(supabase_client: Client, category: str, limit: int = 5):
    try:
        response = supabase_client.table(f"{category}_articles").select("content", "title").limit(limit).execute()
        if response.status_code == 200:
            return response.data
        else:
            print(f"Error retrieving {category} articles: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error retrieving articles from {category}: {e}")
        return []
    
def summarize_with_retrieval_and_rag(supabase_client: Client, query: str, category: str):
    articles = retrieve_articles_from_supabase(supabase_client, category)
    
    if articles:
        retrieved_content = " ".join([article['content'] for article in articles])
        
        full_context = f"Query: {query}\n\n{retrieved_content}"
        
        if category == "sports":
            return sports_summary(full_context)
        elif category == "technology":
            return tech_summary(full_context)
        elif category == "health":
            return health_summary(full_context)
        elif category == "politics":
            return politics_summary(full_context)
        else:
            return "Category not recognized"
    else:
        return "No relevant articles found"
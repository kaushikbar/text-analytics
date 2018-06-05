import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from tqdm import tqdm_notebook
from functools import reduce

def getSources():
    source_url = 'https://newsapi.org/v1/sources?language=en'
    response = requests.get(source_url).json()
    sources = []
    for source in response['sources']:
        sources.append(source['id'])
    return sources

def mapping():
    d = {}
    response = requests.get('https://newsapi.org/v1/sources?language=en')
    response = response.json()
    for s in response['sources']:
        d[s['id']] = s['category']
    return d

def category(source, m):
    try:
        return m[source]
    except:
        return 'NC'

# Link: https://newsapi.org
# Email: biswa.travel@gmail.com
# API key: 47426e078fc74cd1b9f50b844a3d2c92
def getDailyNews():
    sources = getSources()
    key = '47426e078fc74cd1b9f50b844a3d2c92'
    url = 'https://newsapi.org/v1/articles?source={0}&sortBy={1}&apiKey={2}'
    responses = []
    for i, source in tqdm_notebook(enumerate(sources), total=len(sources)):
        
        try:
            u = url.format(source, 'top', key)
        except:
            u = url.format(source, 'latest', key)
        
        response = requests.get(u)
        r = response.json()
        try:
            for article in r['articles']:
                article['source'] = source
            responses.append(r)
        except:
            print('Rate limit exceeded ... please wait and retry in 6 hours')
            return None
                
    articles = list(map(lambda r: r['articles'], responses))
    articles = list(reduce(lambda x,y: x+y, articles))
    
    news = pd.DataFrame(articles)
    news = news.dropna()
    news = news.drop_duplicates()
    news.reset_index(inplace=True, drop=True)
    d = mapping()
    news['category'] = news['source'].map(lambda s: category(s, d))
    news['scraping_date'] = datetime.now()

    try:
        news_df = pd.read_csv('./data/news.csv')
        news_df = news_df.append(news, ignore_index=True)
        news_df = news_df.drop_duplicates('url')
        news_df.reset_index(inplace=True, drop=True)
        news_df.to_csv('./data/news.csv', encoding='utf-8', index=False)
    except:
        news.to_csv('./data/news.csv', index=False, encoding='utf-8')
        
    print('Done')
    
if __name__=='__main__':
    getDailyNews()
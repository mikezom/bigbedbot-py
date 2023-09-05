import feedparser
import random
import time
import json
import requests
from os.path import exists
from bs4 import BeautifulSoup
from graia.ariadne.message.chain import MessageChain
from dateutil import parser
from thefuzz import process
from loguru import logger


SMZDM_UPDATE_INTERVAL = 60*60*2

class SMZDM:
    buffer: dict

    def get_target_index(l: list) -> int:
        if len(l) < 30:
            return len(l)
        else:
            return l.index(min(l))
    
    def time_parser(time: str) -> int:
        date_time = parser.parse(time)
        return int(date_time.timestamp())
    
    @classmethod
    def load_buffer(cls) -> None:
        if not exists('data/smzdm/smzdm.json'):
            cls.buffer = {
                'title': [],
                'link': [],
                'time': [],
                'update_time': 0
            }
        else:
            with open('data/smzdm/smzdm.json') as f:
                cls.buffer = json.load(f)
    
    @classmethod
    def save_buffer(cls) -> None:
        with open('data/smzdm/smzdm.json', 'w+') as f:
            f.write(json.dumps(cls.buffer))
    
    @classmethod
    def update_buffer(cls, title, link, time, i):
        if len(cls.buffer['title']) <= i:
            cls.buffer['title'].append(title)
            cls.buffer['link'].append(link)
            cls.buffer['time'].append(cls.time_parser(time))
        else:
            cls.buffer['title'][i] = title
            cls.buffer['link'][i] = link
            cls.buffer['time'][i] = cls.time_parser(time)
        logger.info(f"updated buffer at {i}: {title}, {time}")

    @classmethod
    def update_smzdm(cls):
        
        cls.load_buffer()
        
        feed = feedparser.parse('http://feed.smzdm.com/')
        
        n = len(feed['entries'])
        
        for i in range(n):
            if feed['entries'][i]['title'] not in cls.buffer['title']:
                target_index = cls.get_target_index(cls.buffer['time'])
                cls.update_buffer(
                    feed['entries'][i]['title'],
                    feed['entries'][i]['link'],
                    feed['entries'][i]['published'],
                    target_index
                )
        
        current_epoch_time = int(time.time())
        cls.buffer['update_time'] = current_epoch_time
        
        cls.save_buffer()
    
    @classmethod
    def check_for_update(cls) -> None:
        cls.load_buffer()
        
        current_epoch_time = int(time.time())
        if current_epoch_time - cls.buffer['update_time'] > SMZDM_UPDATE_INTERVAL:
            cls.update_smzdm()
    
    @classmethod
    def parse_smzdm(cls, m: int = 3) -> MessageChain:
        cls.check_for_update()

        n = len(cls.buffer['title'])
        random_choices = random.choices(range(n), k = m)
        smzdm_string = ""

        for i in random_choices:
            smzdm_string += cls.buffer['title'][i] + "\n"
            smzdm_string += cls.buffer['link'][i] + "\n"
        
        return MessageChain(smzdm_string[:-1])
    
    @classmethod
    def find_smzdm_buffer(cls, s: str) -> MessageChain:
        cls.check_for_update()
        
        fuzz_search_result = process.extract(s, cls.buffer['title'])
        
        smzdm_string = "找到以下结果：\n"
        
        for title, score in fuzz_search_result:
            if score >= 50:
                i = cls.buffer['title'].index(title)
                smzdm_string += cls.buffer['title'][i] + "\n"
                smzdm_string += cls.buffer['link'][i] + "\n"
        
        if len(smzdm_string) == 8:
            return MessageChain(f"没找到")
        else:
            return MessageChain(smzdm_string[:-1])
    
    def search_smzdm(search_str: str) -> MessageChain:
        smzdm_url = 'https://api.smzdm.com/v1/list?'
        request_data = {
            'keyword': search_str,
            'category_id': '',
            'brand_id': '',
            'mall_id': '',
            'order': 'score',
            'limit': 5,
            'offset': '0'
        }

        session = requests.Session()
        session.trust_env = False
        res = session.get(smzdm_url, params = request_data)
        soup = BeautifulSoup(res.content, 'html.parser')
        smzdm_data = json.loads(soup.prettify())
        smzdm_string = ""

        for x in smzdm_data['data']['rows']:
            if x['article_channel_type'] != 'yuanchuang':
                smzdm_string += x['article_title']
                smzdm_string += " " + x['article_price'] + "\n"
                smzdm_string += x['article_url'] + "\n"
        
        return MessageChain(smzdm_string[:-1])
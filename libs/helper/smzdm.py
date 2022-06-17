import feedparser
import random
import time
from graia.ariadne.message.chain import MessageChain

class SMZDM:
    buffer: dict
    last_update = time.struct_time
    
    def need_update() -> bool:
        return True
    
    def parse_smzdm(m: int = 3) -> MessageChain:
        feed = feedparser.parse('http://feed.smzdm.com/')

        n = len(feed['entries'])
        random_choices = random.choices(range(n), k = m)
        smzdm_string = ""

        for i in random_choices:
            smzdm_string += feed['entries'][i]['title'] + "\n"
            smzdm_string += feed['entries'][i]['link'] + "\n"
        
        return MessageChain(smzdm_string[:-1])
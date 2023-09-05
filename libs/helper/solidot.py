import re # Regex
import time # for cache timing
import requests # for html requests
import certifi
from bs4 import BeautifulSoup # html parsing
from graia.ariadne.message.chain import MessageChain  # 信息链

def solidot_update():
    """
    Update solidot news
    """
    solidot_url = 'https://www.solidot.org/'
    res = requests.get(solidot_url, verify=True)
    soup = BeautifulSoup(res.content, 'html.parser')

    global solidot_titles_url
    global solidot_contents
    global solidot_res_title_chain

    solidot_titles_url = []
    solidot_contents = []
    for tag in soup.find_all('a'):
        if(tag.string == '阅读原文'):
            solidot_titles_url.append(tag.get('href'))
    solidot_titles_url = solidot_titles_url[:5]

    solidot_contents.append(int(time.time()))

    solidot_res_title_chain = []

    for i, x in enumerate(solidot_titles_url, 1):
        solidot_article = []
        full_url = solidot_url + x[1:]
        res_full = requests.get(full_url, verify=True)
        soup_full = BeautifulSoup(res_full.content, 'html.parser')

        f_content = soup_full.find('div', class_='p_mainnew')
        str_f = f_content.get_text().translate(
            {ord(i): None for i in '\r\t'}).strip('\n')
        str_f = re.sub(r'(\n)\1+', r'\1', str_f)

        article_time_org = soup_full.find('div', class_='talk_time')
        str_t = article_time_org.get_text()
        str_time = str_t.find('发表于')

        solidot_article.append(soup_full.title.string[12:])    # Title
        solidot_article.append(str_t[str_time: str_time + 26])  # Time
        solidot_article.append(full_url)                       # URL
        solidot_article.append(str_f)                          # Content
        solidot_contents.append(solidot_article)

        solidot_res_title_chain.append(
            str(i) + '.' + soup_full.title.string[12:] + '\n'
        )


def solidot_list() -> MessageChain:
    """
    return recent news titles from solidot
    """
    return MessageChain(solidot_res_title_chain)


def solidot_news(news_code: int) -> MessageChain:
    """return detail of a solidot news report"""
    if not news_code in range(1, 6):
        return MessageChain('Index Out of Range: 正常点！')
    else:
        return MessageChain((solidot_contents[news_code][0] + '\n')
                            + (solidot_contents[news_code][1] + '\n')
                            + (solidot_contents[news_code][2] + '\n')
                            + (solidot_contents[news_code][3][:200] + '...'))


def is_solidot_update_required() -> bool:
    """return a boolean value where current news need update"""
    current_time = int(time.time())
    if (not 'solidot_contents' in globals()) or (len(solidot_contents) == 0):
        return True
    return (current_time - solidot_contents[0]) > 60 * 60 * 2

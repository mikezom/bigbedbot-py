import requests
from lxml import etree
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch
)

from libs.control import Permission

channel = Channel.current()
fname = "data/yecao/cookie.txt"

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("查询流量|流量查询")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try:
        Permission.group_permission_check(group, "liuliang")
    except Exception as e:
        await app.send_group_message(
            group,
            MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()
    
    try: 
        Permission.user_permission_check(member, Permission.DEFAULT)
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"不配：{e}")
        )
    
    liuliang_res = liuliang()
    await app.send_group_message(
        group,
        MessageChain(f"{liuliang_res[0]}\n{liuliang_res[1][:-2]}")
    )

def parseCookieFile(cookiefile):
    cookies = {}
    with open(cookiefile, 'r') as fp:
        sp = fp.read().split(';')
        for x in sp:
            l = x.split('=')
            cookies[l[0]] = l[1]
    return cookies

def liuliang():
    headers = {'User-Agent': 'Mozilla/5.0'}

    my_params = {'action': 'productdetails', 'id': '19731'}
    my_cookies = parseCookieFile(fname)
    res = requests.get('https://www.yecao100.org/clientarea.php', params = my_params, cookies= my_cookies)
    
    r_html = etree.HTML(res.text, etree.HTMLParser())
    
    r1 = r_html.xpath('//*[@class="panel-body"]')
    r11 = r1[1].xpath('string(.)').strip()
    result_string = ''.join(r11.split()).split(';')[1].split('使用详情重置流量')
    result_string[-1] = result_string[-1][:-2] + ' ' + result_string[-1][-2:]
    
    return result_string
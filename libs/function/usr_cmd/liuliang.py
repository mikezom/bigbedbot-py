import requests
import socket
import json
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
    await app.send_group_message(
        group,
        MessageChain(f"这次真的在查了...")
    )
    try:
        liuliang_res = liuliang()
    except:
        await app.send_group_message(
            group,
            MessageChain(f"我靠，又翻车了！")
        )
    await app.send_group_message(
        group,
        MessageChain(f"{liuliang_res[0]}\n{liuliang_res[1][:-2]}")
    )

# def parseCookieFile(cookiefile):
#     cookies = {}
#     with open(cookiefile, 'r') as fp:
#         sp = fp.read().split(';')
#         for x in sp:
#             l = x.split('=')
#             cookies[l[0]] = l[1]
#     return cookies

def liuliang():
    current_ip = socket.getaddrinfo("www.yecao100.org", 80, 0, 0, socket.SOL_TCP)[0][4][0]
    login_address = 'https://' + current_ip + '/dologin.php'
    info_address = 'https://' + current_ip + '/clientarea.php'

    headers = {'User-Agent': 'Mozilla/5.0'}

    session = requests.Session()
    first_res = session.post(login_address, headers=headers)
    r_html = etree.HTML(first_res.text, etree.HTMLParser())
    r1 = r_html.xpath('//*[@name="token"]')
    token = r1[0].values()[2]

    with open('data/yecao/userdata.json', 'r') as f:
        yecao_config_data = json.load(f)
        payload = {
            'username': yecao_config_data["username"],
            'password': yecao_config_data["password"],
            'token': token
        }
        my_params = {
            'action': 'productdetails',
            'id': yecao_config_data["id"]
        }

    session.post(login_address, headers=headers, data=payload)

    my_params = {'action': 'productdetails', 'id': '19731'}
    res = session.get(info_address, params = my_params)

    r_html = etree.HTML(res.text, etree.HTMLParser())
    r1 = r_html.xpath('//*[@class="panel-body"]')
    r11 = r1[1].xpath('string(.)').strip()
    result_string = ''.join(r11.split()).split(';')[1].split('使用详情重置流量')

    return result_string
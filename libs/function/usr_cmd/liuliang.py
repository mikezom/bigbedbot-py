import requests
# import socket
import datetime
import json
import re
from lxml import etree
from loguru import logger
from bisect import bisect_left
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
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
from libs.helper.info import QQInfoConfig

channel = Channel.current()
fname = "data/yecao/cookie.txt"
TRAFFIC_THRESHOLD = [1024, 800, 600, 400, 200, 100, 10, 0]
previous_traffic = -1

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
            MessageChain(f"流量：不配：{e}")
        )
    await app.send_group_message(
        group,
        MessageChain(f"这次真的在查了...")
    )
    try:
        traffic_info, refresh_date = liuliang()
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time
        await app.send_group_message(
            group,
            MessageChain(f"目前剩余流量: {traffic_info[1]}GB, \n还有 {time_difference.days}天{time_difference.seconds // 3600 % 24}小时{time_difference.seconds // 60 % 60}分{time_difference.seconds % 60}秒 刷新流量")
        )
    except:
        await app.send_group_message(
            group,
            MessageChain(f"我靠，又翻车了！")
        )

@channel.use(SchedulerSchema(timers.every_hours())) # Check every HOUR
async def remaining_traffic_warning(app: Ariadne):
    traffic_info, refresh_date = liuliang()
    my_group_info = QQInfoConfig.load_file(714870727, 0)

    if previous_traffic > 0 and traffic_info[1] > previous_traffic:
        # Need Reset
        my_group_info.traffic_threshold_state = 0

    if my_group_info.traffic_threshold_state >= len(TRAFFIC_THRESHOLD):
        # Invalid Save
        logger.error(f"Bad threshold state again, {my_group_info.traffic_threshold_state}")
        my_group_info.traffic_threshold_state = 0

    if traffic_info[1] < TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]:
        # 超了超了
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time
        await app.send_group_message(
            714870727,
            MessageChain(f"流量只剩: {traffic_info[1]}GB了！！！, \n还有 {time_difference.days}天{time_difference.seconds // 3600 % 24}小时{time_difference.seconds // 60 % 60}分{time_difference.seconds % 60}秒 刷新流量")
        )
        # update traffic_threshold_state
        rev_thres = list(reversed(TRAFFIC_THRESHOLD))
        my_group_info.traffic_threshold_state = len(rev_thres) - bisect_left(rev_thres, traffic_info[1])

    logger.info(f"Current threshold for group 714870727 is {TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]}")
    QQInfoConfig.update_file(my_group_info)

    with open('data/yecao/userdata.json', 'r') as f:
        yecao_config_data = json.load(f)
    yecao_config_data["previous_traffic"] = traffic_info[1]
    with open('data/yecao/userdata.json', 'w') as f:
        f.write(json.dumps(yecao_config_data, indent = 4))

def liuliang():
    # current_ip = socket.getaddrinfo("www.yecao100.org", 80, 0, 0, socket.SOL_TCP)[0][4][0]
    current_ip = '47.244.30.150'
    login_address = 'https://' + current_ip + '/dologin.php'
    info_address = 'https://' + current_ip + '/clientarea.php'

    headers = {'User-Agent': 'Mozilla/5.0'}

    session = requests.Session()
    session.trust_env = False
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
        previous_traffic = yecao_config_data["previous_traffic"]

    session.post(login_address, headers=headers, data=payload)

    my_params = {'action': 'productdetails', 'id': '19731'}
    res = session.get(info_address, params = my_params)

    r_html = etree.HTML(res.text, etree.HTMLParser())
    r1 = r_html.xpath('//*[@class="panel-body"]')
    r11 = r1[1].xpath('string(.)').strip()
    r_1 = r11.strip()
    r_2 = r_1.split('\n')
    r_3 = [re.sub('\s+', '', x) for x in r_2]
    traffic_info = [x for x in r_3 if '总共' in x]
    refresh_date = r_3[20]
    traffic_info_match_result = re.findall(r'：(\d*)\(GB\)', traffic_info[0])
    traffic_info_match_result = [int(x) for x in traffic_info_match_result]
    refresh_data_match_result = re.match(r'(\d\d\d\d-\d\d-\d\d)(\d*):(\d*)', refresh_date)
    refresh_date_day = refresh_data_match_result.group(1).split('-')
    refresh_date_day = [int(x) for x in refresh_date_day]
    refresh_date_hour = int(refresh_data_match_result.group(2))
    refresh_date_min = int(refresh_data_match_result.group(3))

    refresh_date_accurate_time = datetime.datetime(*refresh_date_day, refresh_date_hour, refresh_date_min)

    logger.info(f"previous_traffic: {previous_traffic}")

    return traffic_info_match_result, refresh_date_accurate_time
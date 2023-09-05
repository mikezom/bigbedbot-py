import requests
# import socket
import datetime
import dateutil.relativedelta
import json
import re
from loguru import logger
from bisect import bisect_left
from bs4 import BeautifulSoup
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
from libs.helper.info import QQInfoConfig, Type_QQ

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
        traffic_max, traffic_remaining, refresh_date = liuliang()
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time

        last_refresh_time = refresh_date + dateutil.relativedelta.relativedelta(months=-1)
        time_passed = current_time - last_refresh_time
        time_percentage = time_passed / (refresh_date - last_refresh_time)
        expected_traffic_usage = time_percentage * traffic_max
        traffic_usage = traffic_max - traffic_remaining

        traffic_usage_delta = expected_traffic_usage - traffic_usage

        if traffic_usage_delta < 0:
            await app.send_group_message(
                group,
                MessageChain(f"目前剩余流量: {traffic_remaining}GB, \n警惕！！还需要节省{abs(int(traffic_usage_delta))}G\n还有{time_difference.days}天刷新流量")
            )
        else:
            await app.send_group_message(
                group,
                MessageChain(f"目前剩余流量: {traffic_remaining}GB, \n还行哦，还有{abs(int(traffic_usage_delta))}G可以浪\n还有{time_difference.days}天刷新流量")
            )
    except:
        await app.send_group_message(
            group,
            MessageChain(f"我靠，又翻车了！")
        )

@channel.use(SchedulerSchema(timers.every_hours())) # Check every HOUR
async def remaining_traffic_warning(app: Ariadne):
    traffic_max, traffic_current, refresh_date = liuliang()
    my_group_info = QQInfoConfig.load_file(714870727, Type_QQ.GROUP)

    if previous_traffic > 0 and traffic_current > previous_traffic:
        # Need Reset
        my_group_info.traffic_threshold_state = 0

    if my_group_info.traffic_threshold_state >= len(TRAFFIC_THRESHOLD):
        # Invalid Save
        logger.error(f"Bad threshold state again, {my_group_info.traffic_threshold_state}")
        my_group_info.traffic_threshold_state = 0

    if traffic_current < TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]:
        # 超了超了
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time
        await app.send_group_message(
            714870727,
            MessageChain(f"流量只剩: {traffic_current}GB了！！！, \n还有 {time_difference.days}天{time_difference.seconds // 3600 % 24}小时{time_difference.seconds // 60 % 60}分{time_difference.seconds % 60}秒 刷新流量")
        )
        # update traffic_threshold_state
        rev_thres = list(reversed(TRAFFIC_THRESHOLD))
        my_group_info.traffic_threshold_state = len(rev_thres) - bisect_left(rev_thres, traffic_current)

    logger.info(f"Current threshold for group 714870727 is {TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]}")
    QQInfoConfig.update_file(my_group_info)

    with open('data/yecao/userdata.json', 'r') as f:
        yecao_config_data = json.load(f)
    yecao_config_data["previous_traffic"] = traffic_current
    with open('data/yecao/userdata.json', 'w') as f:
        f.write(json.dumps(yecao_config_data, indent = 4))

class SoupParser:
    def parse_token_and_login_addr(sp: BeautifulSoup):
        token = ""
        login_address = ""
        try:
            result = sp.find('input', attrs={'name': 'token'})
            token = result.attrs['value']
        except:
            print(f"unable to get token")

        try:
            result = sp.find_all('form')
            for x in result:
                if 'action' in x.attrs and x.attrs['action'].startswith('https'):
                    login_address = x.attrs['action']
        except:
            print(f"unable to get login address")

        return token, login_address

    def parse_html_table(table) -> list[list]:
        table_data = []
        table_body = table.find('tbody')
        for row in table_body.find_all('tr'):
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            table_data.append([ele for ele in cols if ele])
        return table_data

    @classmethod
    def parse_traffic_info(cls, sp: BeautifulSoup):
        [html_traffic_info_table] = [x for x in sp.find_all('table') if '流量详情' in x.text]
        traffic_info_table = cls.parse_html_table(html_traffic_info_table)

        logger.info(f"Searching: {traffic_info_table[1][0]}")
        # traffic_info_match_result = re.findall(r'：(\d*)\(GB\)', remove_lineswap_and_spaces(traffic_info_table[1][0]))
        traffic_info_match_result = re.findall(r'：(\d*).*', traffic_info_table[1][0])
        [traffic_max, traffic_current] = [int(x) for x in traffic_info_match_result]

        logger.info(f"Searching: {traffic_info_table[3][1]}")
        refresh_time_match_result = re.match(r'(\d\d\d\d-\d\d-\d\d) (\d*):(\d*)', traffic_info_table[3][1])
        refresh_date_day = refresh_time_match_result.group(1).split('-')
        refresh_date_day = [int(x) for x in refresh_date_day]
        refresh_date_hour = int(refresh_time_match_result.group(2))
        refresh_date_min = int(refresh_time_match_result.group(3))

        reset_time = datetime.datetime(*refresh_date_day, refresh_date_hour, refresh_date_min)

        return traffic_max, traffic_current, reset_time

def remove_lineswap_and_spaces(s: str):
    return s.replace("\n", "").replace(" ", "")

def obtain_token_and_login_addr(ses : requests.Session, add, header):
    with ses.post(add, headers=header) as res:
        soup = BeautifulSoup(res.text, 'html.parser')
        token, login_address = SoupParser.parse_token_and_login_addr(soup)
    return token, login_address

def load_config_yecao(path, token):
    payload = {}
    params = {}
    with open(path, 'r') as f:
        yecao_config_data = json.load(f)
        payload = {
            'username': yecao_config_data["username"],
            'password': yecao_config_data["password"],
            'token': token
        }
        params = {
            'action': 'productdetails',
            'id': yecao_config_data["id"]
        }
    return payload, params

def liuliang():
    domain_yecao = 'https://yecao100.org'
    address_obtain_token = domain_yecao + '/dologin.php'
    address_client_info = domain_yecao + '/clientarea.php'

    headers = {
        'User-Agent': 'Mozilla/5.1'
    }
    session = requests.Session()
    session.trust_env = False

    token, login_address = obtain_token_and_login_addr(session, address_obtain_token, headers)
    if token and login_address:
        logger.info(f"[Success] Get token and login address")
    payload, my_params = load_config_yecao('data/yecao/userdata.json', token)
    if payload and my_params:
        logger.info(f"[Success] Get payload and parameters")

    # Logging in
    session.post(login_address, headers=headers, data=payload)

    # Obtain traffic info for certain ID
    with session.get(address_client_info, params = my_params) as res:
        soup = BeautifulSoup(res.text, 'html.parser')
        traffic_max, traffic_current, reset_time = SoupParser.parse_traffic_info(soup)
        logger.info(f"max: {traffic_max}, remain: {traffic_current}, refresh: {reset_time}")

    return traffic_max, traffic_current, reset_time
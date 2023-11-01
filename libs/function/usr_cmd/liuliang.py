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
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from libs.control import Permission
from libs.helper.info import QQInfoConfig, Type_QQ

channel = Channel.current()
fname = "data/yecao/cookie.txt"
TRAFFIC_THRESHOLD = [1024, 800, 600, 400, 200, 100, 10, 0]
previous_traffic = -1

channel.name("liuliang")
channel.description("查询流量剩余")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("查询流量|流量查询")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    await app.send_group_message(group, MessageChain("这次真的在查了..."))
    try:
        traffic_max, traffic_remaining, refresh_date = liuliang()
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time

        last_refresh_time = (
            refresh_date
            + dateutil.relativedelta.relativedelta(months=-1)
        )
        time_passed = current_time - last_refresh_time
        time_percentage = time_passed / (
            refresh_date - last_refresh_time
        )
        expected_traffic_usage = time_percentage * traffic_max
        traffic_usage = traffic_max - traffic_remaining

        traffic_usage_delta = expected_traffic_usage - traffic_usage

        if traffic_usage_delta < -10:
            await app.send_group_message(
                group,
                MessageChain(
                    f"目前剩余流量: {traffic_remaining}GB,"
                    f" \n警惕！！还需要节省{abs(int(traffic_usage_delta))}G\n还有{time_difference.days}天{time_difference.seconds%(60*60*24)//(60*60)}时{time_difference.seconds%(60*60)//(60)}分{time_difference.seconds%60}秒刷新流量"
                ),
            )
        elif traffic_usage_delta > 10:
            await app.send_group_message(
                group,
                MessageChain(
                    f"目前剩余流量: {traffic_remaining}GB, \n还行哦，"
                    f"还有{abs(int(traffic_usage_delta))}G可以浪\n还有{time_difference.days}天{time_difference.seconds%(60*60*24)//(60*60)}时{time_difference.seconds%(60*60)//(60)}分{time_difference.seconds%60}秒刷新流量"
                ),
            )
        else:
            await app.send_group_message(
                group,
                MessageChain(
                    f"目前剩余流量: {traffic_remaining}GB,"
                    f" \n还有{time_difference.days}天{time_difference.seconds%(60*60*24)//(60*60)}时{time_difference.seconds%(60*60)//(60)}分{time_difference.seconds%60}秒刷新流量"
                ),
            )
    except Exception as _:
        await app.send_group_message(group, MessageChain("我靠，又翻车了！"))


# Check traffic every 10 minutes
@channel.use(SchedulerSchema(timers.every_custom_minutes(10)))
async def remaining_traffic_warning(app: Ariadne):
    logger.info("Checking traffic threshold")
    traffic_max, traffic_current, refresh_date = liuliang()
    current_time = datetime.datetime.now()
    time_difference = refresh_date - current_time

    last_refresh_time = (
        refresh_date + dateutil.relativedelta.relativedelta(months=-1)
    )
    time_passed = current_time - last_refresh_time
    time_percentage = time_passed / (refresh_date - last_refresh_time)
    expected_traffic_usage = time_percentage * traffic_max
    traffic_usage = traffic_max - traffic_current

    traffic_usage_delta = expected_traffic_usage - traffic_usage

    # my_group_info = QQInfoConfig.load_file(714870727, Type_QQ.GROUP)
    my_group_info = QQInfoConfig.load_group_info(714870727)
    global previous_traffic
    logger.info(f"previous traffic: {previous_traffic}")
    logger.info(f"current traffic: {traffic_current}")

    # Reset Logic
    if previous_traffic > 0 and traffic_current > previous_traffic:
        # 流量比之前多了，说明流量重置/购买流量包了
        logger.info("Traffic threshold resetting...")
        my_group_info.traffic_threshold_state = 0
    elif (
        traffic_current > 800
        and my_group_info.traffic_threshold_state != 1
    ):
        # 或者流量比较多的时候可以无脑reset
        logger.info("Traffic threshold resetting...")
        my_group_info.traffic_threshold_state = 1

    # Invalid Save Number
    if (
        my_group_info.traffic_threshold_state >= len(TRAFFIC_THRESHOLD)
        or my_group_info.traffic_threshold_state < 0
    ):
        logger.error(
            "Bad threshold state again,"
            f" {my_group_info.traffic_threshold_state}"
        )
        my_group_info.traffic_threshold_state = 0

    # 触发说话的逻辑1: 超过了设定的流量线
    if (
        traffic_current
        < TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]
    ):
        # 超过了一条现在的线
        # TRAFFIC_THRESHOLD = [1024, 800, 600, 400, 200, 100, 10, 0]
        #                         0    1    2    3    4    5   6  7
        logger.info("Exceeded current traffic threshold")
        current_time = datetime.datetime.now()
        time_difference = refresh_date - current_time
        await app.send_group_message(
            714870727,
            MessageChain(
                f"流量只剩: {traffic_current}GB了！！！, \n还有"
                f" {time_difference.days}天{time_difference.seconds%(60*60*24)//(60*60)}时{time_difference.seconds%(60*60)//(60)}分{time_difference.seconds%60}秒刷新流量"
            ),
        )
        # update traffic_threshold_state
        rev_thres = list(reversed(TRAFFIC_THRESHOLD))
        my_group_info.traffic_threshold_state = len(
            rev_thres
        ) - bisect_left(rev_thres, traffic_current)

    # 触发说话的逻辑2: 短时间内使用过多流量
    if previous_traffic > 0 and previous_traffic - traffic_current >= 4:
        if traffic_usage_delta < 25:
            await app.send_group_message(
                714870727, MessageChain(f"有人在用流量下东西！")
            )

    # Update Variables
    logger.info(
        "Current threshold for group 714870727 is"
        f" {TRAFFIC_THRESHOLD[my_group_info.traffic_threshold_state]}"
    )
    # QQInfoConfig.update_file(my_group_info)
    QQInfoConfig.save_group_info()
    previous_traffic = traffic_current


class SoupParser:
    def parse_token_and_login_addr(sp: BeautifulSoup):
        token = ""
        login_address = ""
        try:
            result = sp.find("input", attrs={"name": "token"})
            token = result.attrs["value"]
        except:
            print(f"unable to get token")

        try:
            result = sp.find_all("form")
            for x in result:
                if "action" in x.attrs and x.attrs["action"].startswith(
                    "https"
                ):
                    login_address = x.attrs["action"]
        except:
            print(f"unable to get login address")

        return token, login_address

    def parse_html_table(table) -> list[list]:
        table_data = []
        table_body = table.find("tbody")
        for row in table_body.find_all("tr"):
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            table_data.append([ele for ele in cols if ele])
        return table_data

    @classmethod
    def parse_traffic_info(cls, sp: BeautifulSoup):
        [html_traffic_info_table] = [
            x for x in sp.find_all("table") if "流量详情" in x.text
        ]
        traffic_info_table = cls.parse_html_table(
            html_traffic_info_table
        )

        logger.info(f"Searching: {traffic_info_table[1][0]}")
        # traffic_info_match_result = re.findall(r'：(\d*)\(GB\)', remove_lineswap_and_spaces(traffic_info_table[1][0]))
        traffic_info_match_result = re.findall(
            r"：(\d*).*", traffic_info_table[1][0]
        )
        [traffic_max, traffic_current] = [
            int(x) for x in traffic_info_match_result
        ]

        logger.info(f"Searching: {traffic_info_table[3][1]}")
        refresh_time_match_result = re.match(
            r"(\d\d\d\d-\d\d-\d\d) (\d*):(\d*)",
            traffic_info_table[3][1],
        )
        refresh_date_day = refresh_time_match_result.group(1).split("-")
        refresh_date_day = [int(x) for x in refresh_date_day]
        refresh_date_hour = int(refresh_time_match_result.group(2))
        refresh_date_min = int(refresh_time_match_result.group(3))

        reset_time = datetime.datetime(
            *refresh_date_day, refresh_date_hour, refresh_date_min
        )

        return traffic_max, traffic_current, reset_time


def remove_lineswap_and_spaces(s: str):
    return s.replace("\n", "").replace(" ", "")


def obtain_token_and_login_addr(ses: requests.Session, add, header):
    with ses.post(add, headers=header) as res:
        soup = BeautifulSoup(res.text, "html.parser")
        token, login_address = SoupParser.parse_token_and_login_addr(
            soup
        )
    return token, login_address


def load_config_yecao(path, token):
    payload = {}
    params = {}
    with open(path, "r") as f:
        yecao_config_data = json.load(f)
        payload = {
            "username": yecao_config_data["username"],
            "password": yecao_config_data["password"],
            "token": token,
        }
        params = {
            "action": "productdetails",
            "id": yecao_config_data["id"],
        }
    return payload, params


def liuliang():
    domain_yecao = "https://yecao100.org"
    address_obtain_token = domain_yecao + "/dologin.php"
    address_client_info = domain_yecao + "/clientarea.php"

    headers = {"User-Agent": "Mozilla/5.1"}
    session = requests.Session()
    session.trust_env = False

    token, login_address = obtain_token_and_login_addr(
        session, address_obtain_token, headers
    )
    if token and login_address:
        logger.info("[Success] Get token and login address")
    payload, my_params = load_config_yecao(
        "data/yecao/userdata.json", token
    )
    if payload and my_params:
        logger.info("[Success] Get payload and parameters")

    # Logging in
    session.post(login_address, headers=headers, data=payload)

    # Obtain traffic info for certain ID
    with session.get(address_client_info, params=my_params) as res:
        soup = BeautifulSoup(res.text, "html.parser")
        (
            traffic_max,
            traffic_current,
            reset_time,
        ) = SoupParser.parse_traffic_info(soup)
        logger.info(
            f"max: {traffic_max}, remain: {traffic_current}, refresh:"
            f" {reset_time}"
        )

    traffic_max = int(traffic_max)
    traffic_current = int(traffic_current)
    return traffic_max, traffic_current, reset_time

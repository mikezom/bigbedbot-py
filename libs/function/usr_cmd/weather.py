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
    RegexResult,
    WildcardMatch
)

from libs.control import Permission

import pandas as pd
import requests
import json
import asyncio
from enum import Enum
from loguru import logger

channel = Channel.current()


# Twilight([FullMatch("实时"), "anything" @ WildcardMatch()]),
# Twilight([FullMatch("實時"), "anything" @ WildcardMatch()]),
# Twilight(["anything" @ WildcardMatch(), FullMatch("实时")]),
# Twilight(["anything" @ WildcardMatch(), FullMatch("實時")]),

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["anything" @ WildcardMatch(), FullMatch("实时")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, anything: RegexResult):

    try:
        Permission.group_permission_check(group, "weather")
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
            MessageChain(f"天气: 不配：{e}")
        )

    if not anything.matched or anything.result is None:
        await app.send_group_message(
            group,
            MessageChain(f"你查啥呢")
        )
    else:
        city = anything.result.display.strip()
        logger.info(f"查查 {city}")
        message_chain = get_weather_info(city)

        if message_chain is not None:
            await app.send_group_message(
                group,
                message_chain
            )
        else:
            await app.send_group_message(
                group,
                MessageChain(f"找不到城市：{city}")
            )

class TypeMJSearch(Enum):
    CAR_LIM = 0
    AQI = 1
    LIFE_INDEX = 2
    WARNING = 3
    WEATHER_FORECAST_24H = 4
    WEATHER_FORECAST_15D = 5
    WEATHER_REAL_TIME = 6
    AQI_FORECAST_5D = 7

MJ_TOKEN = [
    "27200005b3475f8b0e26428f9bfb13e9",
    "8b36edf8e3444047812be3a59d27bab9",
    "5944a84ec4a071359cc4f6928b797f91",
    "7ebe966ee2e04bbd8cdbc0b84f7f3bc7",
    "008d2ad9197090c5dddc76f583616606",
    "f9f212e1996e79e0e602b08ea297ffb0",
    "50b53ff8dd7d9fa320d3d3ca32cf8ed1",
    "0418c1f4e5e66405d33556418189d2d0"
]

def mj_router(type_search: TypeMJSearch):
    mj_url = "https://aliv18.mojicb.com/whapi/json/alicityweather/"
    match type_search:
        case TypeMJSearch.CAR_LIM: return mj_url + "limit"
        case TypeMJSearch.AQI: return mj_url + "aqi"
        case TypeMJSearch.LIFE_INDEX: return mj_url + "index"
        case TypeMJSearch.WARNING: return mj_url + "alert"
        case TypeMJSearch.WEATHER_FORECAST_24H: return mj_url + "forecast24hours"
        case TypeMJSearch.WEATHER_FORECAST_15D: return mj_url + "forecast15days"
        case TypeMJSearch.WEATHER_REAL_TIME: return mj_url + "condition"
        case TypeMJSearch.AQI_FORECAST_5D: return mj_url + "aqiforecast5days"

CITY_ID_PATH = 'data/weather/weather_city.csv'

def get_city_id(city: str):

    df = pd.read_csv(CITY_ID_PATH)
    city_id_list = df.loc[df['city_CN'].str.contains(city), 'city_ID']

    return city_id_list

def describe_aqi(aqi: int):
    if aqi <= 50:
        return "一级（优）"
    elif aqi <= 100:
        return "二级（良）"
    elif aqi <= 150:
        return "三级（轻度污染）"
    elif aqi <= 200:
        return "四级（中度污染）"
    elif aqi <= 300:
        return "五级（重度污染）"
    else:
        return "六级（严重污染）"

def get_appcode(path: str):
    with open(path, 'r') as f:
        weather_config_data = json.load(f)
        return weather_config_data['appcode']

def get_weather_info(city: str):

    msg = ""

    id_list = get_city_id(city)

    if (id_list.value_counts == 0):
        return None
    else:

        city_id = str(id_list.values[0])
        logger.info(f"Get CITY_ID: {city_id}")

        session = requests.Session()
        session.trust_env = False

        appcode = get_appcode('data/weather/userdata.json')

        headers = {
            'appcode': appcode,
            'Content-Type': 'application/x-www-form-urlencoded',
            'charset': 'UTF-8',
            'Authorization': 'APPCODE ' + appcode
        }

        real_time_param = {
            'cityId': city_id,
            'token': MJ_TOKEN[TypeMJSearch.WEATHER_REAL_TIME.value]
        }

        aqi_param = {
            'cityId': city_id,
            'token': MJ_TOKEN[TypeMJSearch.AQI.value]
        }

        with session.post(mj_router(TypeMJSearch.WEATHER_REAL_TIME), headers=headers, data=real_time_param) as res:
            try:
                weather_real_time_data = json.loads(res.text)["data"]
            except:
                return None

        with session.post(mj_router(TypeMJSearch.WEATHER_REAL_TIME), headers=headers, data=aqi_param) as res:
            try:
                aqi_data = json.loads(res.text)["data"]
            except:
                return None

        logger.info(weather_real_time_data)
        logger.info(aqi_data)
        msg = f"""{weather_real_time_data['city']['pname']} {weather_real_time_data['city']['secondaryname']} {weather_real_time_data['city']['name']} {weather_real_time_data['condition']['condition']}\n实时温度: {weather_real_time_data['condition']['temp']}°C, 体感温度: {weather_real_time_data['condition']['realFeel']}°C\n湿度: {weather_real_time_data['condition']['humidity']}%,风向: {weather_real_time_data['condition']['windDir']}@{weather_real_time_data['condition']['windLevel']}级\nAQI: {aqi_data['aqi']['value']} {describe_aqi(int(aqi_data['aqi']['value']))}\n空气质量排行: {aqi_data['aqi']['rank']}\n{weather_real_time_data['condition']['tips']}"""

        return MessageChain(msg)
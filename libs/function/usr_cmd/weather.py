from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image as ImageElement
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
import io
from PIL import ImageFont, ImageDraw, Image
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
async def weather_CN(app: Ariadne, member: Member, group: Group, anything: RegexResult):

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
        weather_data = await asyncio.to_thread(get_weather_info, city)

        if weather_data is not None:
            await app.send_group_message(
                group,
                weather_data
            )
        else:
            await app.send_group_message(
                group,
                MessageChain(f"找不到城市：{city}")
            )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("weather"), "anything" @ WildcardMatch()])]
    )
)
async def weather_global(app: Ariadne, member: Member, group: Group, anything: RegexResult):
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
        city, local_names, weather_data = await asyncio.to_thread(get_open_weather_data, city)

        if weather_data is None:
            await app.send_group_message(
                group,
                MessageChain(f"找不到城市：{city}")
            )
        else:
            img = await asyncio.to_thread(render_open_weather_data, city, local_names, weather_data)
            imgByteArr = image_to_byte_array(img)
            await app.send_group_message(
                group,
                MessageChain([ImageElement(data_bytes=imgByteArr)])
            )




OPEN_WEATHER_GRO_URL = "http://api.openweathermap.org/geo/1.0/direct"
OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def image_to_byte_array(image: Image) -> bytes:
    # BytesIO is a file-like buffer stored in memory
    imgByteArr = io.BytesIO()
    # image.save expects a file-like as a argument
    image.save(imgByteArr, format='PNG')
    # Turn the BytesIO object back into a bytes object
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

def get_lat_lon(city: str):
    appid = get_open_weather_api('data/weather/userdata.json')

    params = {
        "q": city,
        "appid": appid,
        "limit": 1,
    }

    with requests.get(OPEN_WEATHER_GRO_URL, params=params) as res:
        try:
            result_data = json.loads(res.text)[0]
            logger.info(f"get_lat_lon: {result_data}")
        except:
            return None, None, None

    if 'local_names' in result_data.keys():
        return result_data["lat"], result_data["lon"], result_data["local_names"]
    else:
        return result_data["lat"], result_data["lon"], result_data

def get_open_weather_data(city: str):

    lat, lon, local_names = get_lat_lon(city)
    if lat is None or lon is None:
        return city, city, None

    appid = get_open_weather_api('data/weather/userdata.json')

    params = {
        "lat": lat,
        "lon": lon,
        "appid": appid,
        "units": "metric",
        "lang": "zh_cn"
    }

    session = requests.Session()
    session.trust_env = False

    with session.get(OPEN_WEATHER_URL, params=params) as res:
        result_data = json.loads(res.text)
        logger.info(f"get_open_weather_data: {result_data}")

    return city, local_names, result_data

def render_open_weather_data(city_name: str, local_names: dict, weather_data: dict):

    text_box = (400, 230)

    image = Image.new("RGB", text_box, (30, 30, 30))
    font_title = ImageFont.truetype("data/fonts/HYWH-65W.ttf", 36)
    font_text = ImageFont.truetype("data/fonts/HYWH-65W.ttf", 24)
    draw = ImageDraw.Draw(image)
    pointer = (10, 10)
    city_name = f"{city_name}"
    draw.text(pointer, city_name, font=font_title, fill=(255, 255, 255))

    (x, y) = draw.textsize(weather_data["weather"][0]["description"], font=font_title)
    pointer = (text_box[0] - x - 10, pointer[1])
    draw.text(pointer, weather_data["weather"][0]["description"], font=font_title, fill=(255, 255, 255))

    pointer = (10, pointer[1] + y + 10)
    if 'ja' in local_names.keys():
        weather_city_name = f"{weather_data['name']}, {local_names['ja']}"
    else:
        weather_city_name = f"{weather_data['name']}"
    draw.text(pointer, weather_city_name, font=font_text, fill=(255, 255, 255))

    pointer = (10, pointer[1] + 34)
    weather_real_time = f"实时温度: {weather_data['main']['temp']}°C"
    draw.text(pointer, weather_real_time, font=font_text, fill=(255, 255, 255))

    pointer = (10, pointer[1] + 34)
    weather_feels_like = f"体感温度: {weather_data['main']['feels_like']}°C"
    draw.text(pointer, weather_feels_like, font=font_text, fill=(255, 255, 255))

    pointer = (10, pointer[1] + 34)
    weather_humidity = f"湿度: {weather_data['main']['humidity']}%"
    draw.text(pointer, weather_humidity, font=font_text, fill=(255, 255, 255))

    pointer = (10, pointer[1] + 34)
    weather_visibility = f"能见度: {weather_data['visibility'] / 1000}km"
    draw.text(pointer, weather_visibility, font=font_text, fill=(255, 255, 255))

    return image

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

def get_open_weather_api(path: str):
    with open(path, 'r') as f:
        weather_config_data = json.load(f)
        return weather_config_data['open_weather_api_key']

def remove_dup_names(names: list):
    new_names = list(dict.fromkeys(names))
    ret_string = ""
    for name in new_names:
        ret_string += name + " "
    return ret_string

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
        msg = f"""{remove_dup_names([weather_real_time_data['city']['pname'], weather_real_time_data['city']['secondaryname'], weather_real_time_data['city']['name']])}{weather_real_time_data['condition']['condition']}\n实时温度: {weather_real_time_data['condition']['temp']}°C, 体感温度: {weather_real_time_data['condition']['realFeel']}°C\n湿度: {weather_real_time_data['condition']['humidity']}%,风向: {weather_real_time_data['condition']['windDir']}@{weather_real_time_data['condition']['windLevel']}级\nAQI: {aqi_data['aqi']['value']} {describe_aqi(int(aqi_data['aqi']['value']))}\n空气质量排行: {aqi_data['aqi']['rank']}\n{weather_real_time_data['condition']['tips']}"""

        return MessageChain(msg)
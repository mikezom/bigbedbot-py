import json
import re

from bilibili_api import live
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (
    FullMatch,
    RegexResult,
    Twilight,
    WildcardMatch,
)
from graia.ariadne.model import Group, Member
from graia.broadcast.exceptions import ExecutionStop
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from loguru import logger

from libs.control import Permission

LIVEDATA_PATH = "data/bilibili_live_monitor/livedata.json"

channel = Channel.current()


########################################################
# Update bilibili live info per minute
#
@channel.use(SchedulerSchema(timers.every_minute()))
async def update_bili_monitor(app: Ariadne):
    now_on_air = await update_bilibili_live_status()
    for room_id, info in now_on_air.items():
        for group_id in info["subscribed_group"]:
            await app.send_group_message(
                group_id,
                MessageChain(
                    f"{info['owner']}开播啦\nhttps://live.bilibili.com/{room_id}"
                ),
            )

    logger.info("Updating bilibili information")


#
#
########################################################


########################################################
#
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("直播监控"), "anything" @ WildcardMatch()])
        ],
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    # Permission
    try:
        Permission.group_permission_check(
            group, "bilibili_live_monitor"
        )
    except Exception as e:
        await app.send_group_message(
            group, MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()

    # Router
    if not anything.matched or anything.result is None:
        await app.send_group_message(group, MessageChain("你要干啥"))
    else:
        cmd = anything.result.display.strip()
        if cmd.startswith("添加"):
            # 添加频道
            m = re.match(
                "添加 +((https://)?live\.bilibili\.com/)?(.+)", cmd
            )
            if m is not None:
                room_id = m[3]
                add_subscription_result = (
                    await add_subscription_room_for_group(
                        room_id, group
                    )
                )
                if add_subscription_result == 1:
                    await app.send_group_message(
                        group, MessageChain(f"添加频道成功")
                    )
                elif add_subscription_result == 2:
                    await app.send_group_message(
                        group, MessageChain(f"找不到频道")
                    )
                elif add_subscription_result == 3:
                    await app.send_group_message(
                        group, MessageChain(f"该频道已经有啦")
                    )
            else:
                await app.send_group_message(
                    group, MessageChain(f"没匹到")
                )
        elif cmd.startswith("移除"):
            # 移除频道
            await app.send_group_message(group, MessageChain(f"还没写"))
        elif cmd.startswith("列表"):
            # 返回列表
            live_status = await get_subscribed_live_status_as_msg(group)

            await app.send_group_message(
                group, MessageChain(live_status)
            )


async def get_subscribed_live_status_as_msg(group: Group):
    # 以发送的形式获取群组订阅的频道信息
    subscribed_live_status = ""
    now_on_air = await update_bilibili_live_status()

    with open(LIVEDATA_PATH, "r") as f:
        livedata = json.load(f)

    for room_id, info in livedata.items():
        if group.id in info["subscribed_group"]:
            if info["live_status"] == 1:
                subscribed_live_status += (
                    f"{room_id}: {info['owner']} 🔴ON AIR\n"
                )
            elif info["live_status"] == 2:
                subscribed_live_status += (
                    f"{room_id}: {info['owner']} 🈲封禁中\n"
                )
            else:
                subscribed_live_status += (
                    f"{room_id}: {info['owner']}\n"
                )

    return subscribed_live_status[:-1]


async def add_subscription_room_for_group(
    room_id: str, group: Group
) -> int:
    # 添加频道
    # 0: unknown error
    # 1: success
    # 2: no such room
    # 3: already exists

    with open(LIVEDATA_PATH, "r") as f:
        livedata = json.load(f)

    if room_id in livedata.keys():
        if group.id in livedata[room_id]["subscribed_group"]:
            return 3
        else:
            livedata[room_id]["subscribed_group"].append(group.id)

    try:
        info = await live.LiveRoom(int(room_id)).get_room_info()

        room_info = {}
        room_info["subscribed_group"] = [group.id]
        room_info["owner"] = info["anchor_info"]["base_info"]["uname"]
        room_info["live_status"] = info["room_info"]["live_status"]

        livedata[room_id] = room_info

        with open(LIVEDATA_PATH, "w") as f:
            f.write(json.dumps(livedata, indent=4))
    except:
        return 2

    return 1


async def update_bilibili_live_status():
    now_on_air = {}

    with open(LIVEDATA_PATH, "r") as f:
        livedata = json.load(f)

    for room_id in livedata.keys():
        info = await live.LiveRoom(int(room_id)).get_room_info()

        if (
            livedata[room_id]["live_status"] == 0
            and info["room_info"]["live_status"] == 1
        ):
            # now on air
            livedata[room_id]["live_status"] = 1
            now_on_air[room_id] = livedata[room_id]
        elif (
            livedata[room_id]["live_status"] == 1
            and info["room_info"]["live_status"] == 0
        ):
            livedata[room_id]["live_status"] = 0
        elif (
            livedata[room_id]["live_status"]
            != info["room_info"]["live_status"]
        ):
            livedata[room_id]["live_status"] = info["room_info"][
                "live_status"
            ]

    with open(LIVEDATA_PATH, "w") as f:
        f.write(json.dumps(livedata, indent=4))

    return now_on_air

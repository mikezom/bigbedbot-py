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
    WildcardMatch,
)

import random

from libs.control import Permission

from libs.helper.fashenme import get_fashenme, get_fashenme_size, read_fashenme, add_fashenme, has_duplicate

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("加发"), "anything" @ WildcardMatch()])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, anything: RegexResult):
    
    try:
        Permission.group_permission_check(group, "fashenme")
    except Exception as e:
        await app.send_group_message(
            group,
            MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()
    
    read_fashenme()
    
    if anything.matched:
        msg = anything.result.display
        if has_duplicate(msg):
            await app.send_group_message(
                group,
                MessageChain(f"{msg}已经有了!!!")
            )
        elif not msg:
            await app.send_group_message(
                group,
                MessageChain(f"Empty string not allowed, minus one social credit")
            )
        elif msg.startswith('什么'):
            await app.send_group_message(
                group,
                MessageChain(f"正确指令为加发，请再试一次~")
            )
        else:
            add_fashenme(msg)
            read_fashenme()
            added_code = get_fashenme_size() - 1
            await app.send_group_message(
                group,
                MessageChain(f"加了加了, 编号为{added_code}~")
            )
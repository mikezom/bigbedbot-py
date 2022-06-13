from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch
)

import random

from libs.control import Permission

from libs.helper.fashenme import get_fashenme, get_fashenme_size, read_fashenme

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("发什么十连")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try:
        Permission.group_permission_check(group, "fashenme")
    except Exception as e:
        await app.send_group_message(
            group,
            MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()
    
    read_fashenme()

    msg_chain = ""
    for r_choice in random.sample(range(get_fashenme_size()), 10):
        msg_chain += (f"{r_choice}. {get_fashenme(r_choice)}\n")
    msg_chain += (f"怎么发什么都要十连！")
    
    await app.send_group_message(
        group,
        MessageChain(msg_chain)
    )
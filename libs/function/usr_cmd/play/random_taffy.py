from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Voice
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
)

from libs.control import Permission
from os import listdir
from random import choice


channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("随机塔菲")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try:
        Permission.group_permission_check(group, "random_taffy")
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
            MessageChain(f"随机塔菲：不配：{e}")
        )
    
    random_sample = choice(listdir('data/play/taffy'))
    my_path = "data/play/taffy/" + random_sample
    await app.send_group_message(
        group,
        MessageChain([Voice(path = my_path)])
    )
        
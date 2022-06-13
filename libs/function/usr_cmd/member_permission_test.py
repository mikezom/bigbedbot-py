import asyncio

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

from libs.control import Permission

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试1")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try: 
        Permission.user_permission_check(member, Permission.GROUP_ADMIN)
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"不配：{e}")
        )
        raise ExecutionStop()
    
    await app.send_group_message(
            group,
            MessageChain(f"测试：群消息，mem_perm = {member.permission}")
        )
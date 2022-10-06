from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
)

from libs.control import Permission
from libs.helper.avatar import generate_avatar_with_flag, get_qq_avatar


channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("/国旗")])
        ]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try:
        Permission.group_permission_check(group, "avatar_flag")
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
            MessageChain(f"国旗：不配：{e}")
        )
    
    avatar = await get_qq_avatar(member.id)
    
    await app.send_group_message(
        group,
        MessageChain([Image(path = generate_avatar_with_flag(avatar))])
    )
        
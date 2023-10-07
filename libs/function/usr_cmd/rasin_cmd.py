from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch,
    RegexResult,
    FullMatch,
    WildcardMatch,
)

from libs.control import Permission
from libs.helper.rasin import get_rasin, change_rasin

channel = Channel.current()

channel.name("rasin")
channel.description("Stamina System for QQ Group")
channel.author("Mikezom")


# 我的体力
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("体力|我的体力|查询体力")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def cmd_get_rasin(app: Ariadne, member: Member, group: Group):
    res = get_rasin(member.id)
    if res == -1:
        await app.send_group_message(group, MessageChain("你是谁？？"))
    elif res == -2:
        await app.send_group_message(
            group, MessageChain("你体力变成了负数，快艾特zom解决吧！")
        )
    else:
        await app.send_group_message(
            group, MessageChain(f"你现在有 {res}/160 体力。")
        )


# [Debug]修改体力
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("给我体力"), "anything" @ WildcardMatch()])
        ],
        decorators=[
            Permission.require_user_perm(Permission.MASTER),
        ],
    )
)
async def cmd_debug_change_rasin(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    if anything.result:
        rasin_delta = int(anything.result.display.strip())
        change_rasin(member.id, rasin_delta)

    await app.send_group_message(
        group, MessageChain(f"你现在有 {get_rasin(member.id)}/160 体力。")
    )

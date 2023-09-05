from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch
)

from libs.control import Permission
from libs.helper.p import get_p, is_received_daily_p, generate_daily_p, change_p, change_daily_p_to_received, reset_has_received_daily_p, get_user_list

channel = Channel.current()

# 我的批
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("我的批|余额")])]
    )
)
async def cmd_find_p(app: Ariadne, member: Member, group: Group):
    try:
        Permission.group_permission_check(group, "p_cmd")
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
            MessageChain(f"你不配用批：{e}")
        )
    await app.send_group_message(
        group,
        MessageChain(f"你现在有 {get_p(member.id)} 批。")
    )

# 领批
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("领批")])]
    )
)
async def cmd_receive_daily_p(app: Ariadne, member: Member, group: Group):
    try:
        Permission.group_permission_check(group, "p_cmd")
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
            MessageChain(f"你不配领批：{e}")
        )

    if is_received_daily_p(member.id):
        await app.send_group_message(
            group,
            MessageChain(f"你今天已经领过批啦！")
        )
    else:
        daily_p = generate_daily_p(member.id)
        change_p(member.id, daily_p)
        change_daily_p_to_received(member.id)

        await app.send_group_message(
            group,
            MessageChain(f"你成功领取了 {daily_p} 批！\n你现在有 {get_p(member.id)} 批。")
        )

# [Debug]重启每日领批
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("刷新每日批池")])]
    )
)
async def cmd_reset_has_received_daily_p(app: Ariadne, member: Member, group: Group):
    try:
        Permission.user_permission_check(member, Permission.MASTER)
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"你不配：{e}")
        )

    reset_has_received_daily_p()
    await app.send_group_message(
        group,
        MessageChain(f"重启！")
    )

# 批榜
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("批榜")])]
    )
)
async def cmd_find_p(app: Ariadne, member: Member, group: Group):
    try:
        Permission.group_permission_check(group, "p_cmd")
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
            MessageChain(f"你不配用批：{e}")
        )

    user_list = get_user_list()
    member_list = await app.get_member_list(group)
    user_ranking = []
    for _member_ in member_list:
        if str(_member_.id) in user_list:
            user_ranking.append((_member_.id, get_p(_member_.id)))
    
    user_ranking.sort(key=lambda x:x[1], reverse=True)
    msg = ""
    for i, (uid, p_uid) in enumerate(user_ranking[:5]):
        _member_ = await app.get_member(group, uid)
        msg += f"{i+1}. {_member_.name} : {p_uid}\n"

    await app.send_group_message(
        group,
        MessageChain(f"你群批榜：\n{msg}")
    )

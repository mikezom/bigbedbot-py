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
    ResultValue,
)

from loguru import logger

from libs.control import Permission
from libs.helper.backpack import (
    grant_player_item,
    get_backpack_brief,
    remove_player_item,
)

channel = Channel.current()


# 查看背包(Brief)
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("背包")])],
    )
)
async def cmd_find_p(app: Ariadne, member: Member, group: Group):
    try:
        Permission.group_permission_check(group, "p_cmd")
    except Exception as e:
        await app.send_group_message(
            group, MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()

    try:
        Permission.user_permission_check(member, Permission.DEFAULT)
    except Exception as e:
        await app.send_group_message(group, MessageChain(f"你不配用：{e}"))

    backpack_brief = get_backpack_brief(member.id)
    if len(backpack_brief) > 0:
        await app.send_group_message(
            group, MessageChain(f"你背包内有\n{backpack_brief}")
        )
    else:
        await app.send_group_message(group, MessageChain("你背包内么的东西啊"))


# 背包详情


# 给玩家发道具
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight.from_command("!给 {pid} {itemid}")],
    )
)
async def cmd_grant_player_item(
    app: Ariadne,
    member: Member,
    group: Group,
    pid: MessageChain = ResultValue(),
    itemid: MessageChain = ResultValue(),
):
    try:
        Permission.user_permission_check(member, Permission.MASTER)
    except Exception as e:
        await app.send_group_message(group, MessageChain(f"你不配用：{e}"))

    target_pid = int(pid.display)
    target_itemid = int(itemid.display)

    logger.info(f"grant {target_pid}, {target_itemid} * {1}")
    grant_player_item(target_pid, target_itemid, 1)

    await app.send_group_message(
        group, MessageChain(f"这人背包里有\n{get_backpack_brief(target_pid)}")
    )


# 给玩家删道具
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight.from_command("!删 {pid} {itemid}")],
    )
)
async def cmd_delete_player_item(
    app: Ariadne,
    member: Member,
    group: Group,
    pid: MessageChain = ResultValue(),
    itemid: MessageChain = ResultValue(),
):
    try:
        Permission.user_permission_check(member, Permission.MASTER)
    except Exception as e:
        await app.send_group_message(group, MessageChain(f"你不配用：{e}"))

    target_pid = int(pid.display)
    target_itemid = int(itemid.display)

    logger.info(f"remove {target_pid}, {target_itemid} * {1}")
    remove_player_item(target_pid, target_itemid, 1)

    await app.send_group_message(
        group, MessageChain(f"这人背包里有\n{get_backpack_brief(target_pid)}")
    )

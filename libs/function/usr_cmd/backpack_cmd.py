from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
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

channel.name("backpack")
channel.description("[group RPG]backpack-related features")
channel.author("Mikezom")

# 查看背包(Brief)
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("背包")])],
        decorators=[
            Permission.require_group_perm(channel.meta['name'], reply=True),
            Permission.require_user_perm(Permission.USER),
        ]
    )
)
async def cmd_find_p(app: Ariadne, member: Member, group: Group):
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
        decorators=[
            Permission.require_user_perm(Permission.MASTER, reply=True),
        ]
    )
)
async def cmd_grant_player_item(
    app: Ariadne,
    member: Member,
    group: Group,
    pid: MessageChain = ResultValue(),
    itemid: MessageChain = ResultValue(),
):
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
        decorators=[
            Permission.require_user_perm(Permission.MASTER, reply=True),
        ]
    )
)
async def cmd_delete_player_item(
    app: Ariadne,
    member: Member,
    group: Group,
    pid: MessageChain = ResultValue(),
    itemid: MessageChain = ResultValue(),
):
    target_pid = int(pid.display)
    target_itemid = int(itemid.display)

    logger.info(f"remove {target_pid}, {target_itemid} * {1}")
    remove_player_item(target_pid, target_itemid, 1)

    await app.send_group_message(
        group, MessageChain(f"这人背包里有\n{get_backpack_brief(target_pid)}")
    )

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
)
from graia.ariadne.message.parser.base import DetectPrefix

from libs.control import Permission
from libs.helper.info import QQInfoConfig

channel = Channel.current()

channel.name("Permission_Test_1005")
channel.description("测试测试测试测试")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试1")])],
        decorators=[Permission.require_user_perm(Permission.GOD)],
    )
)
async def permission_test_member(
    app: Ariadne, member: Member, group: Group
):
    await app.send_group_message(
        group,
        MessageChain(
            f"测试：群消息，mem_perm = {member.permission},"
            f" user_perm={Permission.get(member)}"
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试2")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def permission_test_group(
    app: Ariadne, member: Member, group: Group
):
    await app.send_group_message(group, MessageChain(f"你可以在本群使用此功能"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight.from_command("/info {uid} {key}")],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.MASTER, True),
        ],
    )
)
async def get_user_info(
    app: Ariadne,
    member: Member,
    group: Group,
    message: MessageChain,
    uid: RegexResult,
    key: RegexResult,
):
    uid = uid.result.display
    key = key.result.display
    res = QQInfoConfig.get_user_info(int(uid), key)

    await app.send_group_message(
        group,
        MessageChain([f"[{uid}][{key}]:\n{res}"]),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight.from_command("/ginfo {gid} {key}")
        ],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.MASTER, True),
        ],
    )
)
async def get_group_info(
    app: Ariadne,
    member: Member,
    group: Group,
    message: MessageChain,
    gid: RegexResult,
    key: RegexResult,
):
    gid = gid.result.display
    key = key.result.display
    res = QQInfoConfig.get_user_info(int(gid), key)

    await app.send_group_message(
        group,
        MessageChain([f"[{gid}][{key}]:\n{res}"]),
    )

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
)
from graia.ariadne.message.parser.base import DetectPrefix

from libs.control import Permission
from libs.helper.avatar import (
    generate_avatar_with_img_above,
    get_qq_avatar,
)


channel = Channel.current()

channel.name("avatar_flag")
channel.description("Give your avatar a cute flag")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("/国旗")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def flag(app: Ariadne, member: Member, group: Group):
    avatar = await get_qq_avatar(member.id)

    await app.send_group_message(
        group,
        MessageChain(
            [Image(path=generate_avatar_with_img_above(avatar))]
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("/mtf")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def mtf_flag(app: Ariadne, member: Member, group: Group):
    avatar = await get_qq_avatar(member.id)

    await app.send_group_message(
        group,
        MessageChain(
            [
                Image(
                    path=generate_avatar_with_img_above(
                        avatar,
                        img_path=(
                            "data/avatar/Transgender_Pride_flag.png"
                        ),
                    )
                )
            ]
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
            DetectPrefix("/mtf"),
        ],
    )
)
async def mtf_flag_At(
    app: Ariadne, member: Member, group: Group, message: MessageChain
):
    t_id = member.id
    for e in message:
        if isinstance(e, At):
            t_id = e.target

    avatar = await get_qq_avatar(t_id)

    await app.send_group_message(
        group,
        MessageChain(
            [
                Image(
                    path=generate_avatar_with_img_above(
                        avatar,
                        img_path=(
                            "data/avatar/Transgender_Pride_flag.png"
                        ),
                    )
                )
            ]
        ),
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("/b")])],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def b_game(app: Ariadne, member: Member, group: Group):
    avatar = await get_qq_avatar(member.id)

    await app.send_group_message(
        group,
        MessageChain(
            [
                Image(
                    path=generate_avatar_with_img_above(
                        avatar, img_path="data/avatar/b.png"
                    )
                )
            ]
        ),
    )

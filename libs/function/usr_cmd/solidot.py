from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    WildcardMatch,
)

from libs.control import Permission
from loguru import logger

from libs.helper.solidot import (
    solidot_update,
    solidot_list,
    solidot_news,
    is_solidot_update_required,
)

channel = Channel.current()

channel.name("solidot")
channel.description("News push for solidot")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [FullMatch("solidot"), "anything" @ WildcardMatch()]
            )
        ],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    if not anything.matched:
        if is_solidot_update_required():
            solidot_update()
        msg = solidot_list()
        logger.info(msg)
        await app.send_group_message(group, MessageChain(msg))
    else:
        news_code = int(anything.result.display)
        if is_solidot_update_required():
            solidot_update()
        await app.send_group_message(
            group, MessageChain(solidot_news(news_code))
        )

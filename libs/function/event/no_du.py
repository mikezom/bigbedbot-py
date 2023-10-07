from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    WildcardMatch,
    RegexResult,
)

from libs.control import Permission

channel = Channel.current()

channel.name("no_du")
channel.description("禁嘟")
channel.author("Mikezom")

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["anything" @ WildcardMatch()])],
        decorators=[
            Permission.require_group_perm(channel.meta['name']),
            Permission.require_user_perm(Permission.USER)
        ]
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    if anything.matched:
        msg = anything.result.display
        if "嘟" in msg:
            await app.send_group_message(
                group, MessageChain([At(member), f" 禁嘟"])
            )

from loguru import logger
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
    ParamMatch,
)

from libs.control import Permission

from libs.helper.smzdm import SMZDM

channel = Channel.current()

channel.name("smzdm")
channel.description("什么值得买")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [FullMatch("smzdm"), "arg" @ ParamMatch(optional=True)]
            )
        ],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, arg: RegexResult
):
    if not arg.matched:
        await app.send_group_message(group, SMZDM.parse_smzdm())
    elif arg.matched:
        smzdm_str = arg.result.display
        await app.send_group_message(
            group, SMZDM.search_smzdm(smzdm_str)
        )

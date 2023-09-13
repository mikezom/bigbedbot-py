from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Voice
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexResult,
    WildcardMatch,
)

from libs.control import Permission
from libs.dict_loader import DictData


channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["anything" @ WildcardMatch()])],
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    try:
        Permission.group_permission_check(group, "sample_player")
    except Exception as e:
        raise ExecutionStop()

    try:
        Permission.user_permission_check(member, Permission.DEFAULT)
    except Exception as e:
        raise ExecutionStop()

    if anything.matched:
        msg = anything.result.display
        if msg in DictData.GenshinSample.dictionary.keys():
            my_path = (
                "data/play/samples/"
                + DictData.GenshinSample.dictionary[msg]
                + ".silk"
            )
            await app.send_group_message(
                group, MessageChain([Voice(path=my_path)])
            )

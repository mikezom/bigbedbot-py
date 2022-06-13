import asyncio

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    WildcardMatch,
)

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("公告"), "anything" @ WildcardMatch()])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, anything: RegexResult):

    if anything.matched:
        msg = anything.result.display
        sended = []
        for group in app.get_group_list():
            if group.id in sended:
                continue
            await app.send_group_message(
                group, MessageChain(f"公告 - {group.id}：\n{msg}")
            )
            sended.append(group.id)
            await asyncio.sleep(0.3)
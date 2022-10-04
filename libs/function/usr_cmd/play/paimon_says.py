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
    FullMatch,
    RegexResult,
    RegexMatch,
    WildcardMatch,
)

from libs.control import Permission
from libs.helper.vits.paimon_says import paimon_says

import requests

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(RegexMatch(r".+(说：).+$"))]
    )
)
async def main(app: Ariadne, member: Member, group: Group, message: MessageChain):
    
    try:
        Permission.group_permission_check(group, "paimon_says")
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
            MessageChain(f"不配：{e}")
        )
    
    msg = message.display.strip().lower()
    split_pos = msg.find('说：')
    speaker = msg[:split_pos]
    req_content = msg[split_pos+2:]

    paimon_says(speaker, req_content)
    
    await app.send_group_message(
        group, 
        MessageChain([Voice(path = 'data/play/new_paimon_test.silk')])
    )
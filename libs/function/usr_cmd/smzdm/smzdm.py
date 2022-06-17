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
    RegexMatch,
    RegexResult,
    ParamMatch,
)

from libs.control import Permission

from libs.helper.smzdm import SMZDM

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([
            FullMatch("smzdm"),
            "arg" @ ParamMatch(optional = True)
            ])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, arg: RegexResult):
    
    try:
        Permission.group_permission_check(group, "smzdm")
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
    
    if not arg.matched:
        await app.send_group_message(
            group,
            SMZDM.parse_smzdm()
        )
    elif arg.matched:
        smzdm_str = arg.result.display
        await app.send_group_message(
            group,
            SMZDM.search_smzdm(smzdm_str)
        )
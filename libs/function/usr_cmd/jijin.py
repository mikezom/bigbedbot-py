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
    WildcardMatch
)

from libs.control import Permission

from libs.helper.jijin import jj_search

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("基金"), "anything" @ WildcardMatch()])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, anything: RegexResult):
    
    try:
        Permission.group_permission_check(group, "jijin")
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
            MessageChain(f"基金: 不配：{e}")
        )
    
    if not anything.matched:
        await app.send_group_message(
            group,
            MessageChain(f"保存基金信息开发中...")
        )
    else:
        jjcode = anything.result.display.strip()
        message_chain = jj_search(jjcode)
        
        if message_chain is not None:
            await app.send_group_message(
                group,
                message_chain
            )
        else:
            await app.send_group_message(
                group,
                MessageChain(f"找不到基金：{jjcode}")
            )
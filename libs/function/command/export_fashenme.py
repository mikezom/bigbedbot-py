from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch
)

from libs.control import Permission
from libs.helper.fashenme import read_fashenme, export_fashenme

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("导出发什么")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    
    try: 
        Permission.user_permission_check(member, Permission.MASTER)
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"只有bot拥有者才能导出哦。{e}")
        )
        raise ExecutionStop()
    
    fname = "大床发什么_export"
    read_fashenme()
    res = export_fashenme(fname)
    if res:
        await app.send_group_message(
            group,
            MessageChain(f"成功导出{res}条发什么~")
        )
        
        with open(f"data/fashenme/{fname}.txt", 'r') as fp:
            fsm_data = fp.read()
            await app.upload_file(data = fsm_data, target = group, name = "大床发什么.txt")
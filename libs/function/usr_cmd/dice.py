from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch,
)

from libs.control import Permission
import random

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                RegexMatch(r"\d+(d|D)\d+$")
            ),
        ],
    )
)
async def main(app: Ariadne, member: Member, group: Group, message: MessageChain):
    
    try:
        Permission.group_permission_check(group, "dice")
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
        raise ExecutionStop()

    msg = message.display.strip().lower()
    msg_res = msg.split('d')
    
    n = int(msg_res[0])
    faces = int(msg_res[1])
    
    if n >= 255 or faces >= 1000:
        await app.send_group_message(
            group,
            MessageChain(f"要不你自己搓个骰子耍耍")
        )
        raise ExecutionStop()
    
    rand_result = []
    
    for _ in range(n):
        rand_result.append(random.randint(1, faces))
    
    res_string = ""
    for x in rand_result:
        res_string += (str(x) + ", ")
    res_string = res_string[:-2]
    
    await app.send_group_message(
        group,
        MessageChain(f"你成功掷出了{n}个{faces}面骰，结果为: \n" + res_string + f"\n总和为{sum(rand_result)}")
    )
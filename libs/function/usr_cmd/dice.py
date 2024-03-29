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

channel.name("dice")
channel.description("A simple dice plugin")
channel.author("Mikezom")

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(RegexMatch(r"\d+(d|D)\d+$")),
        ],
        decorators=[
            Permission.require_group_perm(channel.meta['name']),
            Permission.require_user_perm(Permission.USER)
        ]
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, message: MessageChain
):
    msg = message.display.strip().lower()
    msg_res = msg.split("d")

    n = int(msg_res[0])
    faces = int(msg_res[1])

    if n >= 256 or faces >= 1000:
        await app.send_group_message(
            group, MessageChain("要不你自己搓个骰子耍耍")
        )
        raise ExecutionStop()
    elif n <= 0:
        await app.send_group_message(
            group, MessageChain("结果是...1! 没想到吧")
        )
        raise ExecutionStop()
    elif faces == 1:
        await app.send_group_message(
            group, MessageChain("111111111111111111111111")
        )
        raise ExecutionStop()
    elif faces <= 0:
        await app.send_group_message(group, MessageChain("他有脸吗？他没有！"))
        raise ExecutionStop()

    rand_result = []

    for _ in range(n):
        rand_result.append(random.randint(1, faces))

    res_string = ""
    for x in rand_result:
        res_string += str(x) + ", "
    res_string = res_string[:-2]

    sum_string = ""
    if n > 1:
        sum_string = f"\n总和为{sum(rand_result)}"

    await app.send_group_message(
        group,
        MessageChain(
            f"你成功掷出了{n}个{faces}面骰，结果为: \n" + res_string + sum_string
        ),
    )

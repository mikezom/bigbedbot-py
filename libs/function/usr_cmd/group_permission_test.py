import random
from datetime import datetime

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch
from graia.ariadne.message.element import (
    At,
    Plain,
    Image,
    Forward,
    ForwardNode,
)
from graia.ariadne.util.async_exec import io_bound, cpu_bound

from libs.control import Permission

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试2")])],
    )
)
async def main(app: Ariadne, member: Member, group: Group):
    fwd_nodeList = [
        ForwardNode(
            target=member,
            time=datetime.now(),
            message=MessageChain(
                Image(path="test/vision_api_test/random/221.png")
            ),
        )
    ]
    member_list = await app.get_member_list(group)
    for _ in range(3):
        random_member: Member = random.choice(member_list)
        fwd_nodeList.append(
            ForwardNode(
                target=random_member,
                time=datetime.now(),
                message=MessageChain("牛逼"),
            )
        )
    message = MessageChain(Forward(nodeList=fwd_nodeList))
    await app.send_message(group, message)

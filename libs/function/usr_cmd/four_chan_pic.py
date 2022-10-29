import requests

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch
)

from libs.control import Permission

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("random4chan")])]
    )
)
async def main(app: Ariadne, member: Member, group: Group):

    try:
        Permission.group_permission_check(group, "random_4chan_pic")
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"member_permission_test: 不配：{e}")
        )
        raise ExecutionStop()

    getFourChanPic()

    await app.send_group_message(
            group,
            MessageChain(Image(path = 'data/fourchanpic/fourChanPic.jpeg'))
        )

def getFourChanPic():
    fourChanRequestUrl = "https://fca.jethorse.cn/api/four_chan/view/random"
    fourChanPic = requests.get(fourChanRequestUrl).content
    with open('data/fourchanpic/fourChanPic.jpeg', 'wb+') as f:
        f.write(fourChanPic)
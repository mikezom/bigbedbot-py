from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema

import random

from libs.control import Permission

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def main(app: Ariadne, message: MessageChain, group: Group):
    
    if random.randint(0, 1000) == 1:
        try:
            Permission.group_permission_check(group, "repeater")
        except Exception as e:
            raise ExecutionStop()
        
        await app.send_group_message(
            group,
            message.as_sendable()
        )
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.mirai import GroupRecallEvent, FriendRecallEvent
from graia.saya.builtins.broadcast.schema import ListenerSchema

from loguru import logger
from libs.config import BotConfig
from typing import Union, Optional

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupRecallEvent, FriendRecallEvent]
    )
)
async def main(recalled_message: Union[GroupRecallEvent, FriendRecallEvent], app: Ariadne):

    msg = await app.get_message_from_id(recalled_message.message_id)
    if type(recalled_message).__name__ == 'GroupRecallEvent':
        mem = await app.get_member(recalled_message.group.id, recalled_message.author_id)
        await app.send_friend_message(
            BotConfig.master,
            MessageChain(f"{mem.name}({mem.id})刚刚在{recalled_message.group.name}({recalled_message.group.id})撤回了：\n{msg.message_chain.as_sendable()}")
        )
        
    else:
        mem = await app.get_friend(recalled_message.author_id)
        await app.send_friend_message(
            BotConfig.master,
            MessageChain(f"{mem.nickname}({mem.id})刚刚撤回了：\n{msg.message_chain.as_sendable()}")
        )
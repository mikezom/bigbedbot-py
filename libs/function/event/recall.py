from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.mirai import GroupRecallEvent, FriendRecallEvent
from graia.saya.builtins.broadcast.schema import ListenerSchema

from loguru import logger
from libs.config import BotConfig

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupRecallEvent, FriendRecallEvent]
    )
)
async def main(recall_event: GroupRecallEvent | FriendRecallEvent, app: Ariadne):

    if type(recall_event) is GroupRecallEvent:
        msg = await app.get_message_from_id(recall_event.message_id, recall_event.group)
        mem = await app.get_member(recall_event.group.id, recall_event.author_id)
        await app.send_friend_message(
            BotConfig.master,
            [MessageChain(f"{mem.name}({mem.id})刚刚在{recall_event.group.name}({recall_event.group.id})撤回了："),msg.message_chain]
        )
    elif type(recall_event) is FriendRecallEvent:
        mem = await app.get_friend(recall_event.author_id)
        if mem is None:
            await app.send_friend_message(
            BotConfig.master,
            [MessageChain(f"找不到撤回的比(FriendRecallEvent triggered, but unable to find the friend)")]
        )
        else:
            msg = await app.get_message_from_id(recall_event.message_id, mem)
            await app.send_friend_message(
                BotConfig.master,
                [MessageChain(f"{mem.nickname}({mem.id})刚刚撤回了：\n"),msg.message_chain]
            )
    else:
        await app.send_friend_message(
            BotConfig.master,
            [MessageChain(f"有人撤回了怪东西，但是不知道是啥情况(function triggered, but unable to match to correct event type)")]
        )
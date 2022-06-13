from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At, FlashImage, Image
from graia.ariadne.model import Friend, Member, Group
import json


async def process_friend_message(app, msg : MessageChain, user : Friend):
    with open('config/config.json') as f:
        config_data = json.load(f)

    isMaster = config_data['master'] == user.id

    if msg.has("你好"):
        if isMaster:
            await app.send_friend_message(
                user,
                MessageChain(f"{msg.display}喵")
            )
        else:
            await app.send_friend_message(
                user,
                MessageChain(f"don't touch me!")
            )

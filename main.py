from graia.broadcast import Broadcast  # 收发信息
from graia.application import GraiaMiraiApplication, Session  # 初始化bot
from graia.application.message.chain import MessageChain  # 信息链
from graia.application.event.mirai import FriendRecallEvent, GroupRecallEvent, NewFriendRequestEvent # 撤回等情形
import asyncio  # 异步全般
import json

from graia.application.message.elements.internal import FlashImage, Plain, At, Voice_LocalFile
from graia.application.friend import Friend
from graia.application.group import Group, Member

from graia.broadcast.interrupt import InterruptControl
from graia.application.interrupts import GroupMessageInterrupt

# load config file
with open('config/config.json') as f:
    config_data = json.load(f)

# Initializing bot
loop = asyncio.get_event_loop()
bcc = Broadcast(loop = loop)
app = GraiaMiraiApplication(
    broadcast = bcc,
    connect_info = Session(
        host = "http://0.0.0.0:" + config_data['host_port'],
        authKey = config_data['authKey'],
        account = config_data['bot_ID'],
        websocket = config_data['enable_websocket']
    )
)
inc = InterruptControl(bcc)

# 收到好友信息
@bcc.receiver("FriendMessage")
async def friend_message_listener(message: MessageChain, app: GraiaMiraiApplication, friend: Friend):
    process_friend_message(app, message, friend)

# 加好友
@bcc.receiver('NewFriendRequestEvent')
async def new_friend(event: NewFriendRequestEvent):
    process_friend_request(event)

# 群聊
@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, app: GraiaMiraiApplication, group: Group, member: Member):
    process_group_message(app, message, member, group)


@bcc.receiver("MemberJoinEvent")
async def memjoin_listener(app: GraiaMiraiApplication,
                           group: Group,
                           member: Member):
    process_member_join(app, member, group)


# Recall Events
@bcc.receiver("FriendRecallEvent")
async def recal_listener(message: FriendRecallEvent,
                         app: GraiaMiraiApplication):
    process_friend_recall(app, message)

@bcc.receiver('GroupRecallEvent')
async def group_recall(message: GroupRecallEvent,
                       app: GraiaMiraiApplication,
                       group: Group):
    process_group_recall(app, message, group)

app.launch_blocking()
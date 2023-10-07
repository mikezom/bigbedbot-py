from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch

from libs.control import Permission

channel = Channel.current()

channel.name("Permission_Test_1005")
channel.description("测试测试测试测试")
channel.author("Mikezom")

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试1")])],
        decorators=[
            Permission.require_user_perm(Permission.GOD)
        ]
    )
)
async def permission_test_member(app: Ariadne, member: Member, group: Group):
    await app.send_group_message(
        group, MessageChain(f"测试：群消息，mem_perm = {member.permission}, user_perm={Permission.get(member)}")
    )

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("测试2")])],
        decorators=[
            Permission.require_group_perm(channel.meta['name']),
            Permission.require_user_perm(Permission.USER)
        ]
    )
)
async def permission_test_group(app: Ariadne, member: Member, group: Group):
    await app.send_group_message(
        group, MessageChain(f"你可以在本群使用此功能")
    )
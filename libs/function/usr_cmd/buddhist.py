from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
    RegexResult,
)

from libs.control import Permission
import re
import requests

channel = Channel.current()

channel.name("buddhist-says")
channel.description("Translator for 佛曰")
channel.author("Mikezom")

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(FullMatch("佛曰："), "anything" @ WildcardMatch()),
        ],
        decorators=[
            Permission.require_group_perm(channel.meta['name']),
            Permission.require_user_perm(Permission.USER)
        ]
    )
)
async def decoding(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    msg = anything.result.display.strip()
    if len(msg) == 0:
        await app.send_group_message(group, MessageChain(f"看我脸色行事"))
        raise ExecutionStop()

    path = "https://www.keyfc.net/bbs/tools/tudou.aspx"
    decoding_msg = "佛曰：" + msg
    my_params = {"action": "Decode", "orignalMsg": decoding_msg}

    res = requests.post(path, params=my_params)
    result_string = res.content.decode("UTF-8")
    regex_result = re.findall(r"CDATA\[.*\]", result_string)

    decode_result = regex_result[0][6:-2]

    await app.send_group_message(
        group, MessageChain(f"{decode_result}")
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(FullMatch("听佛说："), "anything" @ WildcardMatch()),
        ],
        decorators=[
            Permission.require_group_perm(channel.meta['name']),
            Permission.require_user_perm(Permission.USER)
        ]
    )
)
async def encoding(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    path = "https://www.keyfc.net/bbs/tools/tudou.aspx"
    encoding_msg = anything.result.display.strip()
    my_params = {"action": "Encode", "orignalMsg": encoding_msg}

    res = requests.post(path, params=my_params)
    result_string = res.content.decode("UTF-8")
    regex_result = re.findall(r"CDATA\[.*\]", result_string)

    encode_result = regex_result[0][6:-2]

    await app.send_group_message(
        group, MessageChain(f"{encode_result}")
    )

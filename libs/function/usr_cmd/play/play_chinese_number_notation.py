from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Voice
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    WildcardMatch,
)

from libs.helper import jianpu_to_sound

from libs.control import Permission



channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("播放"), "anything" @ WildcardMatch()])]
    )
)
async def main(app: Ariadne, member: Member, group: Group, anything: RegexResult):
    
    try:
        Permission.group_permission_check(group, "play_chinese_number_notation")
    except Exception as e:
        await app.send_group_message(
            group,
            MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()
    
    try: 
        Permission.user_permission_check(member, Permission.DEFAULT)
    except Exception as e :
        await app.send_group_message(
            group,
            MessageChain(f"播放：不配：{e}")
        )
    
    if anything.matched:
        speed_and_score = anything.result.display
        score_info = speed_and_score.split(';')
        speed = int(score_info[0])
        if speed > 1000 or speed < 1:
            await app.send_group_message(
                group,
                MessageChain(f"Bad Speed")
            )
        else:
            jianpu_to_sound.number_notation_to_silk(speed, score_info[1])
            await app.send_group_message(
                group, 
                MessageChain([Voice(path = 'data/play/sine.silk')])
            )
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
    RegexMatch,
)
# from graia.ariadne.util.async_exec import run_func

from libs.control import Permission
from libs.helper.vits.paimon_says import paimon_says
from libs.helper.VITS_Paimon.new_paimon_says import true_paimon_says
from libs.helper.MoeGoe.my_MoeGoe import my_moegoe

from loguru import logger

genshin_speaker_list = ['派蒙', '凯亚', '安柏', '丽莎', '琴', '香菱', '枫原万叶',
    '迪卢克', '温迪', '可莉', '早柚', '托马', '芭芭拉', '优菈',
    '云堇', '钟离', '魈', '凝光', '雷电将军', '北斗',
    '甘雨', '七七', '刻晴', '神里绫华', '戴因斯雷布', '雷泽',
    '神里绫人', '罗莎莉亚', '阿贝多', '八重神子', '宵宫',
    '荒泷一斗', '九条裟罗', '夜兰', '珊瑚宫心海', '五郎',
    '散兵', '女士', '达达利亚', '莫娜', '班尼特', '申鹤',
    '行秋', '烟绯', '久岐忍', '辛焱', '砂糖', '胡桃', '重云',
    '菲谢尔', '诺艾尔', '迪奥娜', '鹿野院平藏']

nene_speaker_list = ['綾地寧々','朝武芳乃','在原七海','ルイズ','金色の闇','モモ','結城美柑','小茸','唐乐吟','小殷','花玲','八四','수아','미미르','아린','유화','연화','SA1','SA2','SA3','SA4','SA5','SA6']

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(RegexMatch(r".+(说：).+$"))]
    )
)
async def main(app: Ariadne, member: Member, group: Group, message: MessageChain):
    
    try:
        Permission.group_permission_check(group, "paimon_says")
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
            MessageChain(f"说：不配：{e}")
        )
    
    msg = message.display.strip()
    split_pos = msg.find('说：')
    speaker = msg[:split_pos]
    req_content = msg[split_pos+2:]

    if speaker == '派蒙':
        true_paimon_says(req_content)
        logger.info(f"Paimon VITS: {speaker}, {req_content}, length = {len(req_content)}")
    elif speaker in genshin_speaker_list:
        paimon_says(speaker, req_content)
        logger.info(f"Genshin VITS: {speaker}, {req_content}, length = {len(req_content)}")
    elif speaker == '宁宁':
        my_moegoe(nene_speaker_list[0], req_content)
        logger.info(f"MoeGoe VITS: {nene_speaker_list[0]}, {req_content}, length = {len(req_content)}")
    elif speaker in nene_speaker_list:
        my_moegoe(speaker, req_content)
        logger.info(f"MoeGoe VITS: {speaker}, {req_content}, length = {len(req_content)}")
    else:
        paimon_says(speaker, req_content)
        logger.info(f"Genshin VITS: Paimon, {req_content}, length = {len(req_content)}")
    
    if speaker == '派蒙':
        await app.send_group_message(
            group, 
            MessageChain([Voice(path = 'data/play/true_paimon_test.silk')])
        )
    elif speaker == '宁宁' or speaker in nene_speaker_list:
        await app.send_group_message(
            group, 
            MessageChain([Voice(path = 'data/play/nene_test.silk')])
        )
    else:
        await app.send_group_message(
            group, 
            MessageChain([Voice(path = 'data/play/new_paimon_test.silk')])
        )
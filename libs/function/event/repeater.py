from loguru import logger
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema

import random

from libs.control import Permission
from libs.helper.info import *

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def main(app: Ariadne, message: MessageChain, group: Group):
    
    my_group_info = QQInfoConfig.load_file(group.id, 0) # 0 for group
    # logger.info(f"导入群信息完成，在群：{group.id} 的复读计数器为 {my_group_info.repeater_count}")
    
    if my_group_info.repeater_count > 1000:
        logger.error(f"群：{group.id} 的复读计数器不合法，请检查！")
    
    rand_result = random.random()
    threshold = 0.001
    
    if 100 <= my_group_info.repeater_count <= 200:
        threshold += (my_group_info.repeater_count - 100) * 0.001
    elif 200 < my_group_info.repeater_count:
        threshold += (0.1 + (my_group_info.repeater_count - 200) * 0.002)
    
    if rand_result <= threshold:
        my_group_info.update_repeater_count(0)
        
        try:
            Permission.group_permission_check(group, "repeater")
        except Exception as e:
            raise ExecutionStop()
        
        await app.send_group_message(
            group,
            message.as_sendable()
        )
    else:
        my_group_info.increment_repeater_count()
    
    QQInfoConfig.update_file(my_group_info)
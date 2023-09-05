import random
import json
from datetime import datetime
from loguru import logger

from libs.helper.info import QQInfoConfig, QQUser, Type_QQ

USER_INFO_PATH = 'data/info/user_info.json'

def get_rasin(id: int) -> int:
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人")
        return -1
    elif my_user_info.rasin < 0:
        logger.info(f"ID {id} 群友的体力烂了！！")
        return -2
    else:
        logger.info(f"导入体力完成，群友{id}的体力数量为{my_user_info.rasin}")
        return my_user_info.rasin

def change_rasin(id: int, delta: int):
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人")
        return -1
    else:
        logger.info(f"导入体力完成，群友{id}的体力数量为{my_user_info.rasin}")
        if my_user_info.rasin + delta < 0:
            logger.info(f"无法将体力减到负数")
            return -2
        my_user_info.rasin += delta
        QQInfoConfig.update_file(my_user_info)

def increment_rasin_globally():
    with open(USER_INFO_PATH, 'r') as f:
        user_info = json.load(f)
    
    for user in user_info.keys():
        if user_info[user]["rasin"] < 160: user_info[user]["rasin"] += 1

    with open(USER_INFO_PATH, 'w') as f:
        f.write(json.dumps(user_info, indent = 4))
import random
import json
from datetime import datetime
from loguru import logger

from libs.helper.info import QQInfoConfig, QQUser, Type_QQ

USER_INFO_PATH = 'data/info/user_info.json'

def generate_daily_p(id: int, seed_multiplier: int = 1):
    """
    获取某人的每日批, 量为50+1D20.
    """
    random.seed(datetime.now().timestamp())
    daily_p = 50 + random.randint(1, 20)
    return daily_p

def get_p(id: int) -> int:
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人的批")
        return -1
    else:
        logger.info(f"导入批消息完成，群友{id}的批数量为{my_user_info.p_count}")
        return my_user_info.p_count

def is_received_daily_p(id: int) -> bool:
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人")
        return True
    else:
        return my_user_info.has_received_daily_p

def change_daily_p_to_received(id: int) -> int:
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人")
        return 0
    else:
        my_user_info.has_received_daily_p = True
        QQInfoConfig.update_file(my_user_info)
        return 1

def change_p(id: int, delta: int):
    my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    if not isinstance(my_user_info, QQUser):
        logger.info(f"找不到这人的批")
        return -1
    else:
        logger.info(f"导入批消息完成，群友{id}的批数量为{my_user_info.p_count}")
        my_user_info.p_count += delta
        QQInfoConfig.update_file(my_user_info)

def reset_has_received_daily_p():
    with open(USER_INFO_PATH, 'r') as f:
        user_info = json.load(f)
    
    for user in user_info.keys():
        user_info[user]["has_received_daily_p"] = False

    with open(USER_INFO_PATH, 'w') as f:
        f.write(json.dumps(user_info, indent = 4))

def get_user_list():
    with open(USER_INFO_PATH, 'r') as f:
        user_info = json.load(f)
    
    user_list = list(user_info.keys())
    return user_list
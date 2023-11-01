from dataclasses import dataclass
from enum import Enum

from loguru import logger
from numpy.random import choice

import json

from libs.helper.google_sheet_loader import load_sheet
from libs.helper.info import QQInfoConfig, QQUser, Type_QQ

from math import ceil

PROBABILITY = [0.7825, 0.17, 0.03, 0.01, 0.0045, 0.003]
USER_INFO_PATH = 'data/info/user_info.json'

class Chest_Color(Enum):
    blue=0
    purple=1
    pink=2
    red=3
    gold=4
    black=5

@dataclass
class Game_of_Chest:
    items: list[list]
    counters: list
    probabilities: list

    def get_all_items(self, color: str=''):
        color = color.lower()
        if color is None:
            return self.items
        else:
            color = color.lower()
    
    def add_item(self, item):
        if item[1] not in Chest_Color.__members__:
            logger.info(f"Cannot find color of {item[1]}")
        else:
            self.items[Chest_Color[item[1]].value].append(item)
    
    def get_random_item(self, color_option=0):
        """
            color_option:
            - 0 for any color
            - 1 for no-blue
        """
        if color_option == 0:
            colors = choice(list(Chest_Color), 1, p=self.probabilities)
            for c in colors:
                item_indices = choice(len(self.items[c.value]), 1)
                item = self.items[c.value][item_indices[0]]
            return item

chest_rewards: Game_of_Chest = Game_of_Chest(
        items=[[],[],[],[],[],[]], 
        counters=[0, 0, 0, 0, 0, 0],
        probabilities=PROBABILITY)

def reload_all_chest_rewards():
    logger.info("Reloading All Chest Rewards...")
    target_sheet = 'random_chest'

    global chest_rewards

    logger.info(f"Loading {target_sheet}...")
    variable_info, item_info = load_sheet(target_sheet)

    item_info = item_info[1:]
    variable_info = variable_info[0]
    for _item_ in item_info:
        chest_rewards.add_item(_item_)

def get_chest_opened_today(id: int) -> int:
    # my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(id)
    if not isinstance(my_user_info, QQUser):
        logger.error("找不到这人")
        return -1
    else:
        return my_user_info.chest_opened_today

def increment_chest_opened_today(id: int, delta: int=1):
    # my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(id)
    if not isinstance(my_user_info, QQUser):
        logger.error("找不到这人")
        return 0
    else:
        my_user_info.chest_opened_today += delta
    # QQInfoConfig.update_file(my_user_info)
    QQInfoConfig.save_user_info()
    return 1

def total_p_requirement(id: int, n_chest: int, price_chest: int, bonus_threshold: int):
    # my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(id)
    if not isinstance(my_user_info, QQUser):
        logger.error("找不到这人")
        return 0
    chest_opened = my_user_info.chest_opened_today
    price_total = 0
    for _ in range(n_chest):
        if chest_opened < bonus_threshold:
            price_total += ceil(price_chest / 2)
        else:
            price_total += price_chest
        chest_opened += 1
    return price_total

def reset_chest_opened_today():
    # TODO
    with open(USER_INFO_PATH, 'r') as f:
        user_info = json.load(f)
    
    for user in user_info.keys():
        user_info[user]["chest_opened_today"] = 0

    with open(USER_INFO_PATH, 'w') as f:
        f.write(json.dumps(user_info, indent = 4))
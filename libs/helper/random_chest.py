from dataclasses import dataclass
from enum import Enum

from loguru import logger
from numpy.random import choice

from libs.helper.google_sheet_loader import load_sheet

PROBABILITY = [0.7825, 0.17, 0.03, 0.01, 0.0045, 0.003]

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

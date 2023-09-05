import json

from dataclasses import dataclass
from time import time
from typing import Union

from loguru import logger

from libs.helper.backpack import load_backpack
from libs.helper.google_sheet_loader import load_sheet
from libs.helper.info import EnhancedJSONEncoder, Item

PATH_LOCAL_FARMLEVEL = "data/farm_rpg/local_farmlevel.json"
PATH_LOCAL_PLAYERLEVEL = "data/farm_rpg/local_playerlevel.json"
PATH_USERDATA = "data/farm_rpg/userdata.json"

@dataclass
class Position:
    x: int
    y: int

class FarmPlot:
    pos: Position
    crop: Union[Item, None]
    growth_time: int
    reward: int

    def __init__(self, p: Position, crop: Item) -> None:
        self.pos = p
        self.crop = crop
        self.growth_time = 0
        self.reward = 0

class Farm:
    plots: list[FarmPlot]
    level: int
    owner: int
    hund: Union[Item, None]

    def __init__(self, uid: int, level: int=1) -> None:
        width, height = get_farm_size(level)
        self.plots = []
        for x in range(width):
            for y in range(height):
                new_position = Position(x, y)
                new_farmplot = FarmPlot(new_position, None)
                self.plots.append(new_farmplot)
        self.owner = uid
        #TODO Hund
        self.hund = None

    @classmethod
    def from_data(cls, plots, level, owner, hund):
        new_farm = Farm(owner, level)
        new_farm.plots = plots
        new_farm.hund = hund
        return new_farm

    def level_increment(self) -> None:
        pass

    def update(self, time_delta: int) -> None:

        pass

def reload_farm_size_list():
    logger.info("Loading google sheet for farm size")
    variables, content = load_sheet("farm_size")
    content = content[1:]

    local_storage = {
        "reload_time": int(time.time()),
        "level_sheet": content
    }

    with open(PATH_LOCAL_FARMLEVEL, 'w') as f:
        f.write(json.dumps(local_storage, indent=4, cls=EnhancedJSONEncoder))

def reload_player_level_list(): return

def get_farm_size(level: int):
    with open(PATH_LOCAL_FARMLEVEL, 'r') as f:
        farm_size_info = json.load(f)
    for [lv, x, y] in farm_size_info:
        if level == lv:
            return x, y
    return None

def get_current_farm(uid: int):
    with open(PATH_USERDATA, 'r') as f:
        farm_user_data = json.load(f)

    if uid not in farm_user_data.keys():
        new_farm = Farm(uid)
    
    # Record New Farm
    return
def plant_crop(uid: int, itemid: int, p: Position): return
def remove_crop(uid: int, position): return
def steal_crop(uid: int, target_uid: int, p: Position): return
def crop_growth(): return
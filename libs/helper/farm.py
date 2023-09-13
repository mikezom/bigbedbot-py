import json

from dataclasses import dataclass, asdict
from time import time
from typing import Union

from loguru import logger

from libs.helper.backpack import load_backpack, get_item_by_id
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
    has_harvested: bool = False

    def __init__(self, p: Position, crop: Item) -> None:
        self.pos = p
        self.crop = crop
        self.growth_time = 0
        self.reward = 0
    
    @classmethod
    def from_dict(cls, d: dict):
        new_pos = Position(d['pos']['x'], d['pos']['y'])
        new_item = Item(**d['crop']) if len(d['crop']) > 0 else None
        new_farmplot = FarmPlot(new_pos, new_item)
        new_farmplot.growth_time = int(d['growth_time'])
        new_farmplot.reward = int(d['reward'])
        new_farmplot.has_harvested
        return new_farmplot

    def check_growth_stage(self) -> int:
        if self.crop is None:
            return 0
        else:
            _growth_time_ = self.growth_time
            for i, interval in enumerate(self.crop.growth_time, start=1):
                _growth_time_ -= interval
                if _growth_time_ < 0:
                    return i
            return self.crop.growth_stage + 1

    def update(self, time_delta: int) -> None:
        """
            - time_delta: seconds that have passed
        """
        # Update crop, growth time, and reward(if ready to be harvested)
        self.growth_time += time_delta
        current_stage = self.check_growth_stage()
        if current_stage > self.crop.growth_stage and not self.has_harvested:
            # Can be harvested
            self.reward = self.crop.generate_reward()
            self.has_harvested = True

    def todict(self) -> dict:
        new_dict = {}
        new_dict['pos'] = {'x': self.pos.x, 'y': self.pos.y}
        new_dict['crop'] = asdict(self.crop) if isinstance(self.crop, Item) else {}
        new_dict['growth_time'] = self.growth_time
        new_dict['reward'] = self.reward
        new_dict['has_harvested'] = True if self.has_harvested == 'true' else False
        return new_dict

class Farm:
    plots: list[FarmPlot]
    level: int
    owner: int
    hund: Union[Item, None]
    last_update: int

    def __init__(self, uid: int, level: int=1) -> None:
        width, height = get_farm_size(level)
        self.plots = []
        for x in range(width):
            for y in range(height):
                new_position = Position(x, y)
                new_farmplot = FarmPlot(new_position, None)
                self.plots.append(new_farmplot)
        self.level = level
        self.owner = uid
        #TODO Hund
        self.hund = None
        self.last_update = int(time())

    @classmethod
    def from_data(cls, plots, level, owner, hund, last_update):
        new_farm = Farm(owner, level)
        new_farm.plots = plots
        new_farm.hund = hund
        new_farm.last_update = last_update
        return new_farm

    @classmethod
    def from_dict(cls, d: dict):
        farmplots = []
        for farmplot in d['plots']:
            new_farmplot = FarmPlot.from_dict(farmplot)
            farmplots.append(new_farmplot)
        new_hund = Item(**d['hund']) if len(d['hund']) > 0 else None
        new_farm = Farm.from_data(
                farmplots,
                int(d['level']), 
                int(d['owner']),
                new_hund,
                int(d['last_update']))
        return new_farm
    
    def pos_to_index(self, p: Position) -> int:
        w, h = get_farm_size(self.level)
        return p.x * w + p.y
    
    def level_increment(self) -> None:
        pass

    def update(self) -> None:
        time_delta = int(time.time()) - self.last_update
        
        for plot in self.plots:
            plot.update(time_delta)
    
    def steal(self):
        pass

    def todict(self) -> dict:
        new_dict = {}
        new_dict['plots'] = []
        for plot in self.plots:
            new_dict['plots'].append(plot.todict())
        new_dict['level'] = self.level
        new_dict['owner'] = self.owner
        new_dict['hund'] = asdict(self.hund) if isinstance(self.hund, Item) else {}
        new_dict['last_update'] = self.last_update
        return new_dict
    
    def is_position_empty(self, p: Position):
        i = self.pos_to_index(p)
        return self.plots[i].crop is None

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
        # Initialize a new farm
        new_farm = Farm(uid)
    else:
        # load from save
        new_farm = Farm.from_dict(farm_user_data[uid])

    # Record New Farm
    return new_farm

def save_current_farm(farm: Farm, uid: int):
    with open(PATH_USERDATA, 'r') as f:
        farm_info = json.load(f)
    
    farm_info[uid] = farm.todict()

    with open(PATH_USERDATA, 'w') as f:
        f.write(json.dumps(farm_info, indent=4, cls=EnhancedJSONEncoder))

def plant_crop(uid: int, itemid: int, p: Union[Position, None]):
    farm = get_current_farm(uid)
    crop = get_item_by_id(itemid)
    if not crop.type == 'crop':
        logger.error(f"Item to plant not a crop, {crop.type}")
    
    if p is None:
        # plant into the first empty farmplot
        for plot in farm.plots:
            if plot.crop is None:
                # plant the crop
                plot.crop = crop
                plot.growth_time = 0
                plot.reward = 0
                plot.has_harvested = False
                break
    else:
        # check if the specific position is available
        if farm.is_position_empty(p):
            i = farm.pos_to_index(p)
            farm.plots[i].crop = crop
            farm.plots[i].growth_time = 0
            farm.plots[i].reward = 0
            farm.plots[i].has_harvested = False
        else:
            logger.error(f"Unable to plant crop, ({p.x}, {p.y}) not empty")
    
    return

def remove_crop(uid: int, position): return
def steal_crop(uid: int, target_uid: int, p: Position): return

def update_crop(uid: int): 
    farm = get_current_farm(uid)
    farm.update()
    save_current_farm(farm, uid)
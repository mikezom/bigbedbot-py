import json
import time
from loguru import logger
from dataclasses import dataclass

from libs.helper.info import QQInfoConfig, QQUser, Type_QQ, Item, EnhancedJSONEncoder
from libs.helper.backpack import grant_player_item
from libs.helper.p import get_p, change_p
from libs.helper.google_sheet_loader import load_sheet

PATH_LOCAL_SHOPINFO = "data/farm_rpg/local_shopitems.json"
TO_TM_WDAY = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6
}

@dataclass
class ShopItem:
    id: int
    name: str
    type: str
    appearance_date: str
    price: int

    def __post_init__(self):
        self.id = int(self.id)
        self.price = int(self.price)

class ShopItemsList:
    shop_items_list: list[ShopItem]

    def get_shop_items(self, order: str, items_per_page: int, page: int): return

def is_appearance_data_including_today(d: str):
    if d.lower() == "any":
        return True
    elif '-' in d:
        # Specific Date
        current_time = time.localtime()
        date_interval = d.split('-')
        date_start = time.strptime(date_interval[0], '%Y%m%d')
        date_end = time.strptime(date_interval[1], '%Y%m%d')
        return date_start <= current_time and current_time <= date_end
    else:
        # Specific week day
        current_time = time.localtime()
        available_weekdays = d.lower().split(',')
        return current_time.tm_wday in [TO_TM_WDAY[x] for x in available_weekdays]

def reload_shop_item_list():
    logger.info("Loading google sheet for shop...")
    variable_info, item_info = load_sheet('shop')

    item_info = item_info[1:]
    variable_info = variable_info[0]
    items = []
    for _item_ in item_info:
        _new_item_ = {}
        for i, _var_name_ in enumerate(variable_info, start=0):
            _new_item_[_var_name_] = _item_[i]
        if is_appearance_data_including_today(_new_item_["appearance_date"]):
            items.append(_new_item_)

    local_storage = {
        "reload_time": int(time.time()),
        "items": items
    }

    with open(PATH_LOCAL_SHOPINFO, 'w') as f:
        f.write(json.dumps(local_storage, indent=4, cls=EnhancedJSONEncoder))

def load_shop_item_list() -> list[ShopItem]:
    with open(PATH_LOCAL_SHOPINFO, 'r') as f:
        shop_info = json.load(f)

    shop_items_list = []
    for _items_ in shop_info["items"]:
        _new_shopitem_ = ShopItem(**_items_)
        shop_items_list.append(_new_shopitem_)

    return shop_items_list

def purchase_item(uid: int, itemid: int, quantity: int = 1):
    shop_info = load_shop_item_list()

    for item in shop_info:
        logger.info(f"Compraring {itemid} with {item.id}")
        if itemid == item.id and item.price*quantity <= get_p(uid):
            logger.info(f"Now purchasing {item.name}")
            res = grant_player_item(uid, itemid, quantity)
            if res != 1:
                return 0
            else:
                change_p(uid, -item.price*quantity)
                return 1
    return 0
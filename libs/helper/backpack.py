import json
import time
from loguru import logger

from libs.helper.info import (
    QQInfoConfig,
    QQUser,
    Type_QQ,
    Item,
    EnhancedJSONEncoder,
)
from libs.helper.google_sheet_loader import load_sheet

PATH_LOCAL_ITEMINFO = "data/farm_rpg/local_items.json"
PATH_USERINFO = "data/info/user_info.json"

AVAILABLE_TARGETS = [
    "relic",
    "crop",
    "hoe",
    "gloves",
    "hund",
    "item",
    "seed",
]


def load_backpack(id: int) -> list:
    # my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(id)
    if not isinstance(my_user_info, QQUser):
        logger.info("找不到这人")
        return []
    else:
        return my_user_info.backpack


def reload_all_items():
    logger.info("Reloading All Items...")
    item_list = []

    for sheet in AVAILABLE_TARGETS:
        logger.info(f"Loading {sheet}...")
        variable_info, item_info = load_sheet(sheet)

        item_info = item_info[1:]
        variable_info = variable_info[0]
        items = []
        for _item_ in item_info:
            _new_item_ = {}
            for i, _var_name_ in enumerate(variable_info, start=0):
                _new_item_[_var_name_] = _item_[i]
            items.append(_new_item_)

        for item in items:
            new_item = Item(**item)
            new_item.id = int(new_item.id)
            item_list.append(new_item)

    local_storage = {
        "reload_time": int(time.time()),
        "items": item_list,
    }

    with open(PATH_LOCAL_ITEMINFO, "w") as f:
        f.write(
            json.dumps(local_storage, indent=4, cls=EnhancedJSONEncoder)
        )


def load_item() -> list[Item]:
    with open(PATH_LOCAL_ITEMINFO, "r") as f:
        item_info = json.load(f)

    item_list = []
    for item in item_info["items"]:
        new_item = Item(**item)
        new_item.id = int(new_item.id)
        item_list.append(new_item)

    return item_list


def get_item_by_id(item_id: int) -> Item:
    itemlist = load_item()
    for item in itemlist:
        if item.id == item_id:
            return item
    logger.info(f"找不到id为{item_id}的物品")
    return None


def is_player_has_item(pid: int, item: Item):
    # my_user_info = QQInfoConfig.load_file(pid, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(pid)
    if not isinstance(my_user_info, QQUser):
        logger.info("找不到这人")
        return 0
    else:
        logger.info(f"玩家{pid}有没有{item.name}?")
        itemid = item.id
        for itm in my_user_info.backpack:
            if itm.id == itemid and itm.quantity > 0:
                logger.info("有！")
                return 1
        logger.info("没有！")
        return 0


def grant_player_item(pid: int, itemid: int, delta: int):
    """
    Currently we cannot store two items with the same id, but different state.
    """
    if delta < 0:
        return 0  # 怕了还是得单写
    item = get_item_by_id(itemid)
    if item is None:
        return 2
    logger.info(f"正在给玩家{delta}个{item.name}")
    # my_user_info = QQInfoConfig.load_file(pid, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(pid)
    if not isinstance(my_user_info, QQUser):
        logger.info("找不到这人")
        return 3
    else:
        if is_player_has_item(pid, item) == 1:
            itemid = item.id
            for my_itm in my_user_info.backpack:
                if my_itm.id == itemid:
                    my_itm.quantity += delta
            logger.info(my_user_info)
        else:
            new_item = item
            new_item.quantity = delta
            my_user_info.backpack.append(new_item)
        # QQInfoConfig.update_file(my_user_info)
        QQInfoConfig.save_user_info()
        return 1


def remove_player_item(pid: int, itemid: int, quantity: int):
    if quantity < 0:
        return 0
    item = get_item_by_id(itemid)
    if item is None:
        return None
    logger.info(f"正在给玩家删除{quantity}个{item.name}")
    # my_user_info = QQInfoConfig.load_file(pid, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(pid)
    if not isinstance(my_user_info, QQUser):
        logger.info("找不到这人")
        return None
    else:
        if is_player_has_item(pid, item) == 1:
            itemid = item.id
            for my_itm in my_user_info.backpack:
                if my_itm.id == itemid:
                    my_itm.quantity -= quantity
                    if my_itm.quantity <= 0:
                        my_user_info.backpack.remove(my_itm)
            logger.info(my_user_info)
            # QQInfoConfig.update_file(my_user_info)
            QQInfoConfig.save_user_info()
        else:
            return None


def get_backpack_brief(id: int) -> str:
    # my_user_info = QQInfoConfig.load_file(id, Type_QQ.MEMBER)
    my_user_info = QQInfoConfig.load_user_info(id)
    if not isinstance(my_user_info, QQUser):
        logger.info("找不到这人")
        return ""
    else:
        logger.info(
            f"导入背包消息完成，群友{id}的背包内有{len(my_user_info.backpack)}种物品。"
        )
        ret = ""
        for item in my_user_info.backpack:
            logger.info(f"{item.name}, {item.quantity}")
            ret += f"{item.name}, {item.quantity}go\n"
        return ret


def send_item_to_all_players(itemid: int, quantity: int):
    item = get_item_by_id(itemid)
    if item is None:
        return

    u_list = QQInfoConfig.load_user_list()
    for user in u_list:
        grant_player_item(int(user), itemid, quantity)

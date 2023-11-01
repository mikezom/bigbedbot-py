from loguru import logger

# from asyncio import Lock
# from typing import Optional
# from xmlrpc.client import Boolean
# from graia.saya import Channel
# from collections import defaultdict
from typing import Union

# from graia.ariadne.model import Member, MemberPerm, Group
# from graia.broadcast.exceptions import ExecutionStop
# from graia.ariadne.event.message import GroupMessage
# from graia.broadcast.builtin.decorators import Depend
from dataclasses import dataclass, field, is_dataclass, asdict
import json
from enum import Enum
from numpy.random import randint

# from libs.helper.farm import Farm
import pickle

# TRAFFIC_THRESHOLD = [1024, 800, 600, 400, 200, 100, 10]
GROUP_INFO_PATH = "data/info/group_info.json"
GROUP_INFO_PATH_NEW = "data/info/group_info.dat"
USER_INFO_PATH = "data/info/user_info.json"
USER_INFO_PATH_NEW = "data/info/user_info.dat"


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        # elif isinstance(o, Farm):
        #     return Farm.todict(o)
        return super().default(o)


class Type_QQ(Enum):
    GROUP = 0
    MEMBER = 1


@dataclass
class Item:
    id: int
    name: str
    type: str
    description: str = ""
    effect_description: str = ""
    quantity: int = 0
    growth_time: list = field(
        default_factory=lambda: []
    )  # growth time required
    growth_stage: int = 0  # total stages
    reward_min: int = 0
    reward_max: int = 0
    price: int = 0
    corresponding_crop_id: int = 0

    def format_crop(self):
        if (
            isinstance(self.growth_time, str)
            and len(self.growth_time) > 0
        ):
            new_growth_time = [
                int(x) for x in self.growth_time.split(",")
            ]
            self.growth_time = new_growth_time
        if (
            isinstance(self.growth_stage, str)
            and len(self.growth_stage) > 0
        ):
            self.growth_stage = int(self.growth_stage)
        if (
            isinstance(self.reward_min, str)
            and len(self.reward_min) > 0
        ):
            self.reward_min = int(self.reward_min)
        if (
            isinstance(self.reward_max, str)
            and len(self.reward_max) > 0
        ):
            self.reward_max = int(self.reward_max)

    def generate_reward(self):
        rwd = randint(self.reward_min, self.reward_max)
        return rwd


@dataclass
class QQInfo:
    id: int
    nickname: str = ""

    def update_nickname(self, new_nickname: str):
        self.nickname = new_nickname


@dataclass
class QQGroup(QQInfo):
    repeater_count: int = 0
    traffic_threshold_state: int = 0

    def update_repeater_count(self, new_repeater_count: int):
        self.repeater_count = new_repeater_count

    def increment_repeater_count(self):
        self.repeater_count += 1


@dataclass()
class QQUser(QQInfo):
    fsm_count: int = 0
    p_count: int = 0
    has_received_daily_p: bool = False
    rasin: int = 160
    farm_exp: int = 0
    backpack: list[Item] = field(default_factory=lambda: [])
    chest_opened_today: int = 0

    def format_backpack(self):
        new_backpack = []
        for i in self.backpack:
            if isinstance(i, Item):
                continue
            else:
                # logger.info(f"formating one item {i}")
                new_item = Item(**i)
                if new_item.type == "crop":
                    new_item.format_crop()
                new_backpack.append(new_item)
        self.backpack = new_backpack


global_groups_info = {}
global_users_info = {}


class QQInfoConfig:
    @classmethod
    def load_file(cls, id: int, content_type):
        if content_type == Type_QQ.GROUP:
            group_id_string = str(id)
            with open(GROUP_INFO_PATH, "r") as f:
                group_info = json.load(f)
            group_info = cls.refresh_variables_for_groups(group_info)

            with open(GROUP_INFO_PATH, "w") as f:
                f.write(json.dumps(group_info, indent=4))

            if group_id_string not in group_info:
                my_group_info = QQGroup(id)
            else:
                my_group_info = QQGroup(
                    *group_info[group_id_string].values()
                )

            my_group_info.traffic_threshold_state = int(
                my_group_info.traffic_threshold_state
            )
            return my_group_info

        elif content_type == Type_QQ.MEMBER:
            user_id_string = str(id)
            with open(USER_INFO_PATH, "r") as f:
                user_info = json.load(f)

            # 对齐变量
            user_info = cls.refresh_variables_for_users(user_info)

            with open(USER_INFO_PATH, "w") as f:
                f.write(
                    json.dumps(
                        user_info, indent=4, cls=EnhancedJSONEncoder
                    )
                )

            if user_id_string not in user_info:
                my_user_info = QQUser(id)
            else:
                my_user_info = QQUser(
                    *user_info[user_id_string].values()
                )

            my_user_info.format_backpack()

            return my_user_info

    @classmethod
    def load_user_list(cls) -> list[int]:
        lst = []
        with open(USER_INFO_PATH, "r") as f:
            user_info = json.load(f)
        for usr in user_info.keys():
            lst.append(int(usr))
        return lst

    @classmethod
    def refresh_variables_for_groups(cls, group_dict: dict[str, dict]):
        dummy_group = QQGroup(0)
        current_qqgroup_variables = dummy_group.__dict__
        for group_id, group_info in group_dict.items():
            for (
                variable_name,
                variable_default_value,
            ) in current_qqgroup_variables.items():
                if variable_name not in group_info:
                    group_dict[group_id][
                        variable_name
                    ] = variable_default_value
        return group_dict

    @classmethod
    def refresh_variables_for_users(cls, user_dict: dict[str, dict]):
        dummy_user = QQUser(0)
        current_qquser_variables = dummy_user.__dict__
        for user_id, user_info in user_dict.items():
            for (
                variable_name,
                variable_default_value,
            ) in current_qquser_variables.items():
                if variable_name not in user_info:
                    user_dict[user_id][
                        variable_name
                    ] = variable_default_value
        return user_dict

    @classmethod
    def update_file(cls, content: Union[QQGroup, QQUser]):
        if isinstance(content, QQGroup):
            with open(GROUP_INFO_PATH, "r") as f:
                group_info = json.load(f)

            content_id_string = str(content.id)
            if content_id_string not in group_info:
                group_info[content_id_string] = {}

            group_info[content_id_string] = content.__dict__

            with open(GROUP_INFO_PATH, "w") as f:
                f.write(json.dumps(group_info, indent=4))

        elif isinstance(content, QQUser):
            with open(USER_INFO_PATH, "r") as f:
                user_info = json.load(f)

            user_id_string = str(content.id)
            if user_id_string not in user_info:
                user_info[user_id_string] = {}

            user_info[user_id_string] = content.__dict__

            with open(USER_INFO_PATH, "w") as f:
                f.write(
                    json.dumps(
                        user_info, indent=4, cls=EnhancedJSONEncoder
                    )
                )
        else:
            logger.error(
                f"info.py: QQInfoConfig: update_file({type(content)}):"
                " no such content type"
            )

    @classmethod
    def save_group_info(cls):
        global global_groups_info
        with open(GROUP_INFO_PATH_NEW, "wb") as f:
            pickle.dump(global_groups_info, f, protocol=2)

    @classmethod
    def save_user_info(cls):
        global global_users_info
        with open(USER_INFO_PATH_NEW, "wb") as f:
            pickle.dump(global_users_info, f, protocol=2)

    @classmethod
    def load_user_info(cls, uid: int):
        global global_users_info
        if uid not in global_users_info.keys():
            new_user = QQUser(uid)
            global_users_info[uid] = new_user
            cls.save_user_info()
        return global_users_info[uid]

    @classmethod
    def load_group_info(cls, gid: int):
        global global_groups_info
        if gid not in global_groups_info.keys():
            new_group = QQGroup(gid)
            global_groups_info[gid] = new_group
            cls.save_group_info()
        return global_groups_info[gid]

    @classmethod
    def reload_user_info(cls):
        global global_users_info
        with open(USER_INFO_PATH_NEW, "rb") as f:
            global_users_info = pickle.load(f)

    @classmethod
    def reload_group_info(cls):
        global global_groups_info
        with open(GROUP_INFO_PATH_NEW, "rb") as f:
            global_groups_info = pickle.load(f)

    @classmethod
    def write_group_info_to_dat(cls):
        with open(GROUP_INFO_PATH, "r") as f:
            groups_info = json.load(f)

        global global_groups_info
        for group_id, group_info in groups_info.items():
            new_group = QQGroup(*group_info.values())
            global_groups_info[int(group_id)] = new_group

        with open(GROUP_INFO_PATH_NEW, "wb") as f:
            pickle.dump(global_groups_info, f, protocol=2)

    @classmethod
    def write_user_info_to_dat(cls):
        with open(USER_INFO_PATH, "r") as f:
            users_info = json.load(f)

        global global_users_info
        for user_id, user_info in users_info.items():
            new_user = QQUser(*user_info.values())
            new_user.format_backpack()
            global_users_info[int(user_id)] = new_user

        with open(USER_INFO_PATH_NEW, "wb") as f:
            pickle.dump(global_users_info, f, protocol=2)

    @classmethod
    def get_user_info(cls, uid, key):
        global global_users_info
        try:
            res = global_users_info[uid].__dict__[key]
            return res
        except Exception as e:
            return f"Error: {e}"


class GlobalFunction:
    @classmethod
    def increment_rasin(cls):
        global global_users_info
        for id, info in global_users_info.items():
            info.rasin = (
                info.rasin + 1 if info.rasin < 160 else info.rasin
            )
        QQInfoConfig.save_user_info()

    @classmethod
    def reset_daily_p(cls):
        global global_users_info
        for id, info in global_users_info.items():
            info.has_received_daily_p = False
        QQInfoConfig.save_user_info()

from loguru import logger
# from asyncio import Lock
# from typing import Optional
# from xmlrpc.client import Boolean
# from graia.saya import Channel
# from collections import defaultdict
from typing import DefaultDict, Set, Tuple, Union
# from graia.ariadne.model import Member, MemberPerm, Group
# from graia.broadcast.exceptions import ExecutionStop
# from graia.ariadne.event.message import GroupMessage
# from graia.broadcast.builtin.decorators import Depend
from dataclasses import dataclass
import json
from enum import Enum

# TRAFFIC_THRESHOLD = [1024, 800, 600, 400, 200, 100, 10]

class Type_QQ(Enum):
    GROUP = 0
    MEMBER = 1

@dataclass
class QQInfo:
    id: int
    nickname: str = ""

    def update_nickname(self, new_nickname: str): self.nickname = new_nickname


@dataclass
class QQGroup(QQInfo):
    repeater_count: int = 0
    traffic_threshold_state: int = 0

    def update_repeater_count(self, new_repeater_count: int): self.repeater_count = new_repeater_count
    def increment_repeater_count(self): self.repeater_count += 1

@dataclass()
class QQUser(QQInfo):
    fsm_count: int = 0

class QQInfoConfig:

    @classmethod
    def load_file(cls, id, content_type):
        if content_type == 0:
            # group
            group_id_string = str(id)
            with open('data/info/group_info.json', 'r') as f:
                group_info = json.load(f)
            group_info = cls.refresh_variables_for_groups(group_info)

            with open('data/info/group_info.json', 'w') as f:
                f.write(json.dumps(group_info, indent = 4))

            if group_id_string not in group_info:
                my_group_info = QQGroup(id)
            else:
                my_group_info = QQGroup(*group_info[group_id_string].values())

            return my_group_info

        elif content_type == 1:
            # user
            user_id_string = str(id)
            with open('data/info/user_info.json', 'r') as f:
                user_info = json.load(f)

            if user_id_string not in user_info:
                my_user_info = QQUser(id)
            else:
                my_user_info = QQUser(id,
                                      user_info[user_id_string]["nickname"],
                                      user_info[user_id_string]["fsm_count"])

            return my_user_info

    @classmethod
    def refresh_variables_for_groups(cls, group_dict: dict[str, dict]):
        dummy_group = QQGroup(0)
        current_qqgroup_variables = dummy_group.__dict__
        for group_id, group_info in group_dict.items():
            for variable_name, variable_default_value in current_qqgroup_variables.items():
                if variable_name not in group_info:
                    group_dict[group_id][variable_name] = variable_default_value
        return group_dict

    @classmethod
    def update_file(cls, content: Union[QQGroup, QQUser]):
        if type(content) is QQGroup:
            with open('data/info/group_info.json', 'r') as f:
                group_info = json.load(f)

            content_id_string = str(content.id)
            if content_id_string not in group_info:
                group_info[content_id_string] = {}

            group_info[content_id_string] = content.__dict__

            with open('data/info/group_info.json', 'w') as f:
                f.write(json.dumps(group_info, indent = 4))


        elif type(content) is QQUser:
            with open('data/info/user_info.json', 'r+') as f:
                user_info = json.load(f)

            user_id_string = str(content.id)
            if user_id_string not in user_info:
                user_info[user_id_string] = {}

            user_info[user_id_string]["nickname"] = content.nickname
            user_info[user_id_string]["fsm_count"] = content.fsm_count

            with open('data/info/user_info.json', 'w') as f:
                f.write(json.dumps(user_info, indent = 4))
        else:
            logger.error(f"info.py: QQInfoConfig: update_file({type(content)}): no such content type")
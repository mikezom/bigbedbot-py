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

@dataclass
class QQInfo:
    id: int
    nickname: str
    
    def update_nickname(self, new_nickname: str): self.nickname = new_nickname
            

@dataclass
class QQGroup(QQInfo):
    repeater_count: int
    
    def update_repeater_count(self, new_repeater_count: int): self.repeater_count = new_repeater_count
    def increment_repeater_count(self): self.repeater_count += 1

@dataclass
class QQUser(QQInfo):
    fsm_count: int

class QQInfoConfig:
    
    @classmethod
    def load_file(cls, id, content_type):
        if content_type == 0:
            # group
            group_id_string = str(id)
            with open('data/info/group_info.json', 'r') as f:
                group_info = json.load(f)
            
            if group_id_string not in group_info:
                my_group_info = QQGroup(id, "", 0)
            else:
                my_group_info = QQGroup(id, group_info[group_id_string]["nickname"], group_info[group_id_string]["repeater_count"])
            
            return my_group_info
    
    @classmethod
    def update_file(cls, content: Union[QQGroup, QQUser]):
        if type(content) is QQGroup:
            with open('data/info/group_info.json', 'r') as f:
                group_info = json.load(f)
                
            content_id_string = str(content.id)
            if content_id_string not in group_info:
                group_info[content_id_string] = {}
            
            group_info[content_id_string]["nickname"] = content.nickname
            group_info[content_id_string]["repeater_count"] = content.repeater_count
            
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
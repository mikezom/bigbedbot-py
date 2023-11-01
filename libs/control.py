import time

from asyncio import Lock
from typing import Optional
from xmlrpc.client import Boolean
from graia.saya import Channel
from collections import defaultdict
from typing import DefaultDict, Set, Tuple, Union
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Member, MemberPerm, Group
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.builtin.decorators import Depend

import json

from libs.config import BotConfig

channel = Channel.current()


class Permission:
    """
    用于管理权限的类，不应被实例化
    """

    GOD = 999
    MASTER = 30
    GROUP_ADMIN = 20
    USER = 10
    BANNED = 0
    DEFAULT = USER

    @classmethod
    def get(cls, member: Union[Member, int]) -> int:
        """
        获取用户的权限

        :param user: 用户实例或QQ号
        :return: 等级，整数
        """

        if isinstance(member, Member):
            user = member.id
            user_permission = member.permission
        if isinstance(member, int):
            user = member
            user_permission = cls.DEFAULT

        if user == 80000000:
            raise ExecutionStop()

        if user in BotConfig.admins:
            return cls.MASTER
        elif user in BotConfig.bans:
            return cls.BANNED
        elif user_permission in [MemberPerm.Administrator, MemberPerm.Owner]:
            return cls.GROUP_ADMIN
        else:
            return cls.DEFAULT

    @classmethod
    def get_group_permission(cls, group: Group, cmd: str) -> Boolean:
        '''
        返回群是否被允许使用功能
        '''
        
        groupID = str(group.id)
        
        with open('config/group_permissions.json') as f:
            group_config_data = json.load(f)

            if groupID not in group_config_data:
                group_config_data[groupID] = {}
            
            if cmd not in group_config_data[groupID]:
                # 默认启用功能
                group_config_data[groupID][cmd] = True

        with open('config/group_permissions.json', 'w') as f:
            f.write(json.dumps(group_config_data, indent=4))
        
        return group_config_data[groupID][cmd]

    @classmethod
    def get_corresponding_cmd(cls, msg: str):
        '''
        可能应该搬到其他地方
        '''
        with open('config/function_name.json') as f:
            function_names = json.load(f)
            
        if msg not in function_names:
            raise Exception()
        else:
            return function_names[msg]["name"]

    @classmethod
    def change_group_permission(cls, group: Group, cmd: str, isAllowed: Boolean):
        '''
        开启/关闭群功能
        '''
        
        groupID = str(group.id)
        
        with open('config/group_permissions.json') as f:
            group_config_data = json.load(f)

        if groupID not in group_config_data:
            group_config_data[groupID] = {}
        
        group_config_data[groupID][cmd] = isAllowed

        with open('config/group_permissions.json', 'w') as f:
            f.write(json.dumps(group_config_data, indent=4))

    @classmethod
    def require_user_perm(cls, level: int, reply:bool=False):
        async def require_user_perm_deco(app: Ariadne, group: Group, user: Member):
            member_level = cls.get(user)
            if member_level < level:
                if reply:
                    await app.send_message(group, MessageChain("你不配啊你不配"))
                raise ExecutionStop
        return Depend(require_user_perm_deco)

    @classmethod
    def require_group_perm(cls, cmd: str, reply:bool=False):
        async def require_group_perm_deco(app: Ariadne, group: Group):
            # isTestGroup = group.id in BotConfig.Debug.groups
            isAllowed = cls.get_group_permission(group, cmd)
            
            if not isAllowed:
                if reply:
                    await app.send_message(group, MessageChain("本群不开放此功能"))
                raise ExecutionStop
        return Depend(require_group_perm_deco)

    @classmethod
    def user_permission_check(cls, member: Member, level: int = DEFAULT):

        member_level = cls.get(member)

        if (
            (
                # Debug模式开启，不在Debug群里
                BotConfig.Debug.enable
                and member.group.id not in BotConfig.Debug.groups
            )
            or (
                # 普通权限不够
                member_level < level
            )
        ):
            raise ExecutionStop(f"权限不够，debug模式开启情况：{BotConfig.Debug.enable}。你的权限是{member_level}，需要{level}。")

    @classmethod
    def group_permission_check(cls, group: Group, cmd: str):
        '''
        群是否开放功能
        debug群开放所有功能
        '''
        
        isTestGroup = group.id in BotConfig.Debug.groups
        isAllowed = cls.get_group_permission(group, cmd)
        
        if (
            (not isTestGroup)
            and (not isAllowed)
        ):
            raise ExecutionStop(f"isTestGroup = {isTestGroup}, isAllowed = {isAllowed}")

class Interval:
    """
    用于冷却管理的类，不应被实例化
    ! NOT WORKING !
    """

    last_exec: DefaultDict[int, Tuple[int, float]] = defaultdict(lambda: (1, 0.0))
    sent_alert: Set[int] = set()
    lock: Optional[Lock] = None

    @classmethod
    async def get_lock(cls):
        if not cls.lock:
            cls.lock = Lock()
        return cls.lock

    @classmethod
    async def require(
        cls,
        suspend_time: float = 10,
        max_exec: int = 1,
        override_level: int = Permission.MASTER,
    ):
        """
        指示用户每执行 `max_exec` 次后需要至少相隔 `suspend_time` 秒才能再次触发功能
        等级在 `override_level` 以上的可以无视限制
        :param suspend_time: 冷却时间
        :param max_exec: 在再次冷却前可使用次数
        :param override_level: 可超越限制的最小等级
        """

        async def cd_check(event: GroupMessage):
            if Permission.get(event.sender) >= override_level:
                return
            current = time.time()
            async with (await cls.get_lock()):
                last = cls.last_exec[event.sender.id]
                if current - cls.last_exec[event.sender.id][1] >= suspend_time:
                    cls.last_exec[event.sender.id] = (1, current)
                    if event.sender.id in cls.sent_alert:
                        cls.sent_alert.remove(event.sender.id)
                    return
                elif last[0] < max_exec:
                    cls.last_exec[event.sender.id] = (last[0] + 1, current)
                    if event.sender.id in cls.sent_alert:
                        cls.sent_alert.remove(event.sender.id)
                    return
                if event.sender.id not in cls.sent_alert:
                    cls.sent_alert.add(event.sender.id)
                raise ExecutionStop()

        return Depend(cd_check)

    @classmethod
    async def manual(
        cls,
        member: Union[Member, int],
        suspend_time: float = 10,
        max_exec: int = 1,
        override_level: int = Permission.MASTER,
    ):
        if Permission.get(member) >= override_level:
            return
        current = time.time()
        async with (await cls.get_lock()):
            last = cls.last_exec[member]
            if current - cls.last_exec[member][1] >= suspend_time:
                cls.last_exec[member] = (1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            elif last[0] < max_exec:
                cls.last_exec[member] = (last[0] + 1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            if member not in cls.sent_alert:
                cls.sent_alert.add(member)
            raise ExecutionStop()
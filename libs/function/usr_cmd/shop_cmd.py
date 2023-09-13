from asyncio import TimeoutError
from creart import create
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from loguru import logger
from libs.control import Permission
from libs.helper.p import get_p
from libs.helper.shop import load_shop_item_list, purchase_item
from libs.helper.backpack import get_backpack_brief

channel = Channel.current()
inc = create(InterruptControl)


# 我的批
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch("商店")])],
    )
)
async def cmd_shop(app: Ariadne, member: Member, group: Group):
    try:
        Permission.group_permission_check(group, "shop_cmd")
    except Exception as e:
        await app.send_group_message(
            group, MessageChain(f"本群不开放此功能，错误信息：{e}")
        )
        raise ExecutionStop()

    try:
        Permission.user_permission_check(member, Permission.DEFAULT)
    except Exception as e:
        await app.send_group_message(group, MessageChain(f"你不配用：{e}"))

    shop_items = load_shop_item_list()

    # Need optimization
    msg = ""
    for i, item in enumerate(shop_items, start=1):
        msg += f"{i}. {item.name} 单价{item.price}批\n"

    await app.send_group_message(
        group, MessageChain(f"今日商店: \n{msg}购买请输入商品编号。")
    )

    @Waiter.create_using_function([GroupMessage])
    async def shop_water(g: Group, m: Member, msg: MessageChain):
        if group.id == g.id and member.id == m.id:
            return msg

    try:
        ret_msg = await inc.wait(shop_water, timeout=30)
    except TimeoutError:
        logger.info(f"shop timeout by {member.id}")
    else:
        target_item = int(ret_msg.display.strip())
        ret = purchase_item(member.id, shop_items[target_item - 1].id)

        if ret:
            await app.send_message(
                group,
                MessageChain(
                    f"购买1个{shop_items[target_item-1].name}成功！"
                ),
            )
        else:
            await app.send_message(group, MessageChain(f"你批不够！！"))

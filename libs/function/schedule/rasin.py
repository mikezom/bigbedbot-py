from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from loguru import logger

from libs.helper.rasin import increment_rasin_globally

channel = Channel.current()


@channel.use(SchedulerSchema(timers.every_custom_minutes(8)))
async def recover_rasin(app: Ariadne):
    increment_rasin_globally()
    logger.info("体力恢复中")
    # 需要增加回满体力订阅

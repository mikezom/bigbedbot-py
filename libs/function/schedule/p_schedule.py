from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from libs.helper.p import reset_has_received_daily_p
from libs.helper.random_chest import reset_chest_opened_today

channel = Channel.current()


@channel.use(SchedulerSchema(timers.crontabify("0 0 * * * 0")))
async def wake_up(app: Ariadne):
    reset_has_received_daily_p()
    reset_chest_opened_today()

    await app.send_group_message(714870727, MessageChain(f"每日领批刷新啦"))

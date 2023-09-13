from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

channel = Channel.current()


@channel.use(SchedulerSchema(timers.crontabify("0 9 * * 1-5 0")))
async def wake_up(app: Ariadne):
    await app.send_group_message(714870727, MessageChain("起床上班了！！！！"))


@channel.use(SchedulerSchema(timers.crontabify("0 20 * * 1-5 0")))
async def wake_down(app: Ariadne):
    await app.send_group_message(714870727, MessageChain("下班记得打卡"))

from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema
from graia.ariadne.message.element import Face

from libs.control import Permission

channel = Channel.current()

@channel.use(SchedulerSchema(timers.crontabify("0 9 * * * 0")))
async def main(app: Ariadne):
    await app.send_group_message(
        479733965,
        MessageChain(f"Hey, wake up", Face(277))
    )
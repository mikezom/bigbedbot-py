from loguru import logger
from graia.saya import Saya
from graia.ariadne.app import Ariadne
from prompt_toolkit.styles import Style
from graia.ariadne.console import Console
from graia.scheduler import GraiaScheduler
from prompt_toolkit.formatted_text import HTML
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.scheduler.saya import GraiaSchedulerBehaviour
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.ariadne.entry import config, HttpClientConfig, WebsocketClientConfig

import asyncio
import contextlib

from libs.config import BotConfig

# Initializing bot
host = BotConfig.Mirai.mirai_host
app = Ariadne(
    config(
        BotConfig.Mirai.account,
        BotConfig.Mirai.verify_key,
        HttpClientConfig(host),
        WebsocketClientConfig(host)
    ),
)

console = Console(
    broadcast=app.broadcast,
    prompt=HTML("<bbbot> BBbot </bbbot>> "),
    style=Style(
        [
            ("bbbot", "fg:#ffffff"),
        ]
    ),
)


app.create(GraiaScheduler)
saya = app.create(Saya)
saya.install_behaviours(
    app.create(BroadcastBehaviour),
    app.create(GraiaSchedulerBehaviour),
    ConsoleBehaviour(console),
    app.create(InterruptControl),
)


with saya.module_context():
    saya.require("libs.function.command.announcement")
    saya.require("libs.function.command.function_off")
    saya.require("libs.function.command.function_on")
    saya.require("libs.function.command.export_fashenme")

    # saya.require("libs.function.event.bot_launch")

    saya.require("libs.function.usr_cmd.member_permission_test")
    # saya.require("libs.function.usr_cmd.group_permission_test")
    saya.require("libs.function.event.recall")

    saya.require("libs.function.event.repeater")
    saya.require("libs.function.event.sample_player")
    saya.require("libs.function.event.no_du")

    saya.require("libs.function.usr_cmd.fashenme.fashenme")
    saya.require("libs.function.usr_cmd.fashenme.fashenme_add")
    # saya.require("libs.function.usr_cmd.fashenme.fashenme_remove")
    # saya.require("libs.function.usr_cmd.fashenme.fashenme_too_long")

    saya.require("libs.function.usr_cmd.play.play_chinese_number_notation")
    saya.require("libs.function.usr_cmd.play.play_abc_notation")
    saya.require("libs.function.usr_cmd.play.random_taffy")
    saya.require("libs.function.usr_cmd.play.paimon_says")

    saya.require("libs.function.usr_cmd.solidot")

    saya.require("libs.function.usr_cmd.jijin")

    saya.require("libs.function.usr_cmd.liuliang")

    saya.require("libs.function.usr_cmd.smzdm.smzdm")

    saya.require("libs.function.usr_cmd.avatar.flag")

    saya.require("libs.function.usr_cmd.dice")

    saya.require("libs.function.usr_cmd.buddhist")

    saya.require("libs.function.usr_cmd.four_chan_pic")

    saya.require("libs.function.schedule.wake_up")

with contextlib.suppress(KeyboardInterrupt, asyncio.exceptions.CancelledError):
    app.launch_blocking()
logger.info("BBbot is shutting down...")
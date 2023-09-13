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
# import pkgutil
import os

from libs.config import BotConfig
from libs.helper.backpack import reload_all_items
from libs.helper.shop import reload_shop_item_list
from libs.helper.random_chest import reload_all_chest_rewards

UNWANTED_FEATURE = [
    'group_permission_test',
    'fashenme_remove',
    'fashenme_too_long',
    'paimon_says'
]

def is_feature_unwanted(name):
    for i in UNWANTED_FEATURE:
        if i in name:
            return True
    return False

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
    for root, dirs, files in os.walk("libs/function"):
        for name in files:
            p = os.path.join(root, name)
            if not p.endswith("py") or is_feature_unwanted(p):
                continue
            p = p[:-3].replace('/', '.')
            saya.require(p)

    reload_all_items()
    reload_shop_item_list()
    reload_all_chest_rewards()

with contextlib.suppress(KeyboardInterrupt, asyncio.exceptions.CancelledError):
    app.launch_blocking()
logger.info("BBbot is shutting down...")
import asyncio
import contextlib
import os

from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleBehaviour
from graia.ariadne.entry import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.broadcast.interrupt import InterruptControl
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.scheduler import GraiaScheduler
from graia.scheduler.saya import GraiaSchedulerBehaviour
from loguru import logger
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from libs.config import BotConfig
from libs.helper.backpack import reload_all_items
from libs.helper.random_chest import reload_all_chest_rewards
from libs.helper.shop import reload_shop_item_list
from libs.helper.info import QQInfoConfig

UNWANTED_FEATURE = [
    "group_permission_test",
    "fashenme_remove",
    "fashenme_too_long",
    "paimon_says",
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
        WebsocketClientConfig(host),
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
            p = p[:-3].replace("/", ".")
            saya.require(p)

    reload_all_items()
    reload_shop_item_list()
    reload_all_chest_rewards()
    # QQInfoConfig.write_group_info_to_dat()
    # QQInfoConfig.write_user_info_to_dat()
    QQInfoConfig.reload_user_info()
    QQInfoConfig.reload_group_info()

with contextlib.suppress(
    KeyboardInterrupt, asyncio.exceptions.CancelledError
):
    app.launch_blocking()
logger.info("BBbot is shutting down...")

from graia.ariadne.app import Ariadne
from graia.ariadne.console import Console
from graia.ariadne.console.saya import ConsoleSchema
from graia.ariadne.message.parser.base import MatchContent
from graia.saya import Channel

from prompt_toolkit.styles import Style

from libs.helper.info import QQInfoConfig

channel = Channel.current()


@channel.use(ConsoleSchema([MatchContent("stop")]))
async def stop(app: Ariadne, console: Console):
    res: str = await console.prompt(
        l_prompt=[("class:warn", " 你确定要退出吗? "), ("", " (y/n) ")],
        style=Style([("warn", "bg:#cccccc fg:#d00000")]),
    )
    if res.lower() in ("y", "yes"):
        # Save player's information
        QQInfoConfig.save_group_info()
        QQInfoConfig.save_user_info()
        app.stop()
        console.stop()

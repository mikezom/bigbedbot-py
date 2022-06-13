import json

from pydantic import AnyHttpUrl

# load config file
with open('config/config.json') as f:
    config_data = json.load(f)
    
class BotConfig:
    class Mirai:
        account: int = config_data["mirai"]["bot_ID"]
        verify_key: str = config_data["mirai"]["authKey"]
        mirai_host: AnyHttpUrl = config_data["mirai"]["mirai_host"]
    
    class Debug:
        enable: bool = config_data["debug"]["enable"]
        groups: list[int] = config_data["debug"]["groups"]
    
    name: str = config_data["name"]
    master: int = config_data["master"]
    admins: list[int] = config_data["admins"]
    bans: list[int] = config_data["bans"]
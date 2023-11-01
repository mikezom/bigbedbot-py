from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    WildcardMatch,
)

from libs.control import Permission

import openai
import json
import asyncio
import time
from loguru import logger

TIMEOUT = 60 * 30
HISTORY_PATH = "data/openAI/chat_history.json"


def get_openai_api_key(path: str):
    with open(path, "r") as f:
        openai_config_data = json.load(f)
        return openai_config_data["OPENAI_API_KEY"]


openai.organization = ""
openai.api_base = "https://api.nova-oss.com/v1"
openai.api_key = get_openai_api_key("data/openAI/userinfo.json")

channel = Channel.current()

channel.name("chatGPT")
channel.description("Yet Another ChatGPT Plugin")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch(">"), "anything" @ WildcardMatch()])
        ],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def main(
    app: Ariadne,
    member: Member,
    group: Group,
    anything: RegexResult,
    message: GroupMessage,
):
    if not anything.matched or anything.result is None:
        await app.send_group_message(group, MessageChain("你问啥呢"))
    else:
        prompt_msg = anything.result.display.strip()

        if is_end_of_chat(prompt_msg):
            clear_chat_history(member.id, HISTORY_PATH)
            await app.send_group_message(
                group, MessageChain("End of This Conversation")
            )
        else:
            message_bundle = []
            chat_history = load_chat_history(member.id, HISTORY_PATH)

            if chat_history is None or chat_history == {}:
                clear_chat_history(member.id, HISTORY_PATH)
                message_bundle = [
                    {"role": "user", "content": prompt_msg}
                ]
            else:
                history_time, history_chat = (
                    float(chat_history["time"]),
                    chat_history["chat"],
                )
                if (
                    is_timeout(history_time)
                    or history_chat is None
                    or len(history_chat) == 0
                ):
                    clear_chat_history(member.id, HISTORY_PATH)
                    message_bundle = [
                        {"role": "user", "content": prompt_msg}
                    ]
                else:
                    message_bundle = chat_history["chat"]
                    message_bundle.append(
                        {"role": "user", "content": prompt_msg}
                    )

            logger.info(f"问问 {message_bundle}")

            gpt_msg_ret = await asyncio.to_thread(
                ask_chatGPT, message_bundle
            )

            if gpt_msg_ret is not None:
                message_bundle.append(
                    {"role": "assistant", "content": gpt_msg_ret}
                )
                save_chat_history(
                    member.id, HISTORY_PATH, message_bundle
                )
                await app.send_group_message(
                    group, MessageChain(gpt_msg_ret), quote=message.id
                )
            else:
                await app.send_group_message(
                    group,
                    MessageChain("烂了，可能需要>end清除消息记录"),
                )


def is_end_of_chat(msg: str):
    if msg.lower() == "end of chat" or msg.lower() == "end":
        return True
    else:
        return False


def ask_chatGPT(prompt_msg: list, model: str = "gpt-4-0613"):
    try:
        res = openai.ChatCompletion.create(
            model=model, messages=prompt_msg
        )
        content = res.choices[0].message.content  # type: ignore
        return content
    except Exception:
        return None


def load_chat_history(qq_id: int, history_path: str):
    with open(history_path, "r") as f:
        openai_chat_history = json.load(f)

    try:
        chat_history = openai_chat_history[str(qq_id)]
        return chat_history
    except Exception:
        return None


def save_chat_history(qq_id: int, history_path: str, chat_history):
    with open(history_path, "r") as f:
        openai_chat_history = json.load(f)

    openai_chat_history[str(qq_id)] = {
        "time": time.time(),
        "chat": chat_history,
    }

    with open(history_path, "w+") as f:
        json.dump(openai_chat_history, f, indent=4)


def clear_chat_history(qq_id: int, history_path: str):
    with open(history_path, "r") as f:
        openai_chat_history = json.load(f)

    openai_chat_history[str(qq_id)] = {}

    with open(history_path, "w+") as f:
        json.dump(openai_chat_history, f, indent=4)


def is_timeout(t: float):
    current_time = time.time()
    if current_time - t > TIMEOUT:
        return True
    else:
        return False

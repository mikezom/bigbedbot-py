from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.broadcast.exceptions import ExecutionStop
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
    RegexResult,
)

import random

from libs.control import Permission

from libs.helper.fashenme import (
    get_fashenme,
    get_fashenme_size,
    read_fashenme,
    find_fashenme,
    find_fashenme_how_many,
)

channel = Channel.current()

channel.name("fashenme")
channel.description("random fashenme")
channel.author("Mikezom")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("发什么"), "anything" @ WildcardMatch()])
        ],
        decorators=[
            Permission.require_group_perm(channel.meta["name"]),
            Permission.require_user_perm(Permission.USER),
        ],
    )
)
async def main(
    app: Ariadne, member: Member, group: Group, anything: RegexResult
):
    read_fashenme()

    if not anything.matched:
        random_choice = random.randrange(0, get_fashenme_size())

        await app.send_group_message(
            group, MessageChain(f"{get_fashenme(random_choice)}")
        )

    else:
        to_search = anything.result.display

        if to_search == "十连":
            msg_chain = ""
            for r_choice in random.sample(
                range(get_fashenme_size()), 10
            ):
                msg_chain += f"{get_fashenme(r_choice)}\n"
            msg_chain += "怎么发什么都要十连！"

            await app.send_group_message(group, MessageChain(msg_chain))
        elif to_search.isdigit():
            await app.send_group_message(
                group, MessageChain(f"{get_fashenme(int(to_search))}")
            )
        elif to_search.startswith("多少"):
            await app.send_group_message(
                group,
                MessageChain(
                    f"{find_fashenme_how_many(to_search[2:])}"
                ),
            )
        else:
            await app.send_group_message(
                group, MessageChain(f"{find_fashenme(to_search)}")
            )

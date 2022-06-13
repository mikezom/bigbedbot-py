from graia.ariadne.entry import Ariadne, Friend, MessageChain, config


app = Ariadne(
    config(
        verify_key="1234567890",
        account=2420862130,
    )
)


@app.broadcast.receiver("FriendMessage")
async def friend_message_listener(app: Ariadne, friend: Friend):
    await app.send_message(friend, "Hello, World!")


Ariadne.launch_blocking()
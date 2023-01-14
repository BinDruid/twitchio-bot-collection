import os
from utils.chat_message import ChatMessage
from twitchio.ext.commands import cooldown, command, Bot, Context, Bucket


class Moderator(Bot):
    def __init__(self):
        super().__init__(
            token=os.environ["TOKEN"],
            client_id=os.environ["CLIENT_ID"],
            prefix=os.environ["BOT_PREFIX"],
            initial_channels=[os.environ["CHANNEL"]],
        )

    async def event_ready(self):
        print(f"Logged in as | {self.nick}")

    async def event_message(self, context: Context):
        if context.echo:
            return

        await self.handle_commands(context)
        message = ChatMessage(context.content.lower())
        await self.check_forbidden(context, message)
        await self.check_trigger(context, message)

    async def check_forbidden(self, context: Context, message: ChatMessage):
        if message.has_forbidden_word():
            print("Not OK")
        return

    async def check_trigger(self, context: Context, message: ChatMessage):
        if message.has_trigger_word():
            print("docLeave")
        return

    @cooldown(rate=5, per=60, bucket=Bucket.channel)
    @command(name="ping")
    async def ping(self, context: Context):
        await context.send("pong!")

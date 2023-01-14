import os
from twitchio.ext.commands import Bot, Context


class Crawler(Bot):
    def __init__(self):
        super().__init__(
            token=os.environ["TOKEN"],
            client_id=os.environ["CLIENT_ID"],
            prefix=os.environ["BOT_PREFIX"],
            initial_channels=[os.environ["CHANNEL"]],
        )

    async def event_ready(self):
        print(f"Logged in as < {self.nick} >")

    async def event_message(self, context: Context):
        if context.echo:
            return
        if "custom-reward-id" in context.tags:
            return

        self.save_context(context)
        # await self.handle_commands(context)

    def save_context(self, context: Context):
        print(f"{context.tags['display-name']}: {context.content}")

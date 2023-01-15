import os
from twitchio.ext.commands import Bot
from src.mixins.context import AdvancedContext


class CommonBot(Bot):
    def __init__(self):
        super().__init__(
            token=os.environ["TOKEN"],
            client_id=os.environ["CLIENT_ID"],
            prefix=os.environ["BOT_PREFIX"],
            initial_channels=[os.environ["CHANNEL"]],
        )

    async def get_context(self, message, cls=AdvancedContext) -> AdvancedContext:
        return await super().get_context(message, cls=cls)

    async def event_ready(self):
        print(
            f"< {self.nick} > logged into < {','.join(self._connection._initial_channels)} > "
        )

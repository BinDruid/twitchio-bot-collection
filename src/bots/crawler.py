from src.mixins.database import DataBaseProcessMixin
from .common import CommonBot, AdvancedContext


class Crawler(DataBaseProcessMixin, CommonBot):
    async def event_ready(self):
        await super().event_ready()
        await self.init_database_routine()

    async def event_message(self, message):
        if message.echo:
            return

        context = await self.get_context(message)

        if context.is_reward_redemption:
            return

        self.save_context(context)

    def save_context(self, context: AdvancedContext):
        username = context.message.tags["display-name"]
        message = context.message.content
        self.insert_into_messages(username, message)
        print(f"{username}: {message}")

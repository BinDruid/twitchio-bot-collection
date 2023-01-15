from src.mixins.database_process import DataBaseProcessMixin
from .common import CommonBot, AdvancedContext


class Crawler(DataBaseProcessMixin, CommonBot):
    async def event_ready(self):
        await super().event_ready()
        self.init_database_routine()

    async def event_message(self, message):
        if message.echo:
            return

        context = await self.get_context(message)

        if context.is_reward_redemption:
            return

        self.save_context(context)

    def save_context(self, context: AdvancedContext):
        print(f"{context.message.tags['display-name']}: {context.message.content}")
        self.insert_into_messages(
            context.message.tags["display-name"], context.message.content
        )

from src.mixins.database import DataBaseProcessMixin
from .common import CommonBot, AdvancedContext


class Crawler(DataBaseProcessMixin, CommonBot):
    async def event_ready(self):
        await super().event_ready()
        await self.init_database_routine()
        print("Bot is listening to chat events!")

    async def get_prefix(self, message):
        """
        Forcing crawl bot to ignore user commands started with prefix
        """
        return None

    async def event_message(self, message):
        if message.echo:
            return
        context = await self.get_context(message)

        if context.is_reward_redemption:
            return

        self.save_context(context)

    def save_context(self, context: AdvancedContext):
        self.insert_into_chats_table(context)
        print(f"{context.author['name']}: {context.message.content}")

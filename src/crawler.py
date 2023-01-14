from utils.mixins import CommonBot, AdvancedContext


class Crawler(CommonBot):
    async def event_message(self, message):
        if message.echo:
            return

        context = await self.get_context(message)

        if context.is_reward_redemption:
            return

        self.save_context(context)

    def save_context(self, context: AdvancedContext):
        print(f"{context.message.tags['display-name']}: {context.message.content}")

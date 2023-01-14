from utils.mixins import CommonBot, AdvancedContext
from twitchio.ext.commands import cooldown, command, Bucket


class Moderator(CommonBot):
    async def event_message(self, message):
        if message.echo:
            return
        context = await self.get_context(message)

        await self.handle_commands(message)
        await self.check_forbidden(context)
        await self.check_trigger(context)

    async def check_forbidden(self, context: AdvancedContext):
        if context.has_forbidden_word:
            print("Not OK")
        return

    async def check_trigger(self, context: AdvancedContext):
        if context.has_trigger_word:
            print("docLeave")
        return

    @cooldown(rate=5, per=60, bucket=Bucket.channel)
    @command(name="ping")
    async def ping(self, context: AdvancedContext):
        await context.send("pong!")

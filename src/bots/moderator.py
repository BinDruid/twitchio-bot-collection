from twitchio.ext.commands import cooldown, command, Bucket
from .common import CommonBot, AdvancedContext


class Moderator(CommonBot):
    async def event_message(self, message):
        if message.echo:
            return
        context = await self.get_context(message)
        # await context.send(message.content)
        # await context.channel.send(message.content)

        await self.handle_commands(message)
        await self.check_forbidden(context)
        await self.check_trigger(context)

    async def check_forbidden(self, context: AdvancedContext):
        if context.has_forbidden_word:
            await context.send(f"delete")

    async def check_trigger(self, context: AdvancedContext):
        if context.has_trigger_word:
            await context.send(f"timeout")
        return

    @cooldown(rate=5, per=60, bucket=Bucket.channel)
    @command(name="ping")
    async def ping(self, context: AdvancedContext):
        await context.send("pong!")

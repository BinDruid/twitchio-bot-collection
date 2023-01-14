import os
from twitchio.ext.commands import Bot, Context
from configs.words_lookup import blacklist_words, trigger_words


class TextProcessMixin:
    @property
    def tokens(self):
        return self.message.content.lower().split(" ")

    @property
    def has_forbidden_word(self):
        return self._check_words_in(blacklist_words)

    @property
    def has_trigger_word(self):
        return self._check_words_in(trigger_words)

    def _check_words_in(self, word_list):
        for word in self.tokens:
            if word in word_list:
                return True
        return False

    @property
    def is_reward_redemption(self):
        return "custom-reward-id" in self.message.tags


class AdvancedContext(TextProcessMixin, Context):
    pass


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

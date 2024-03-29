from twitchio.ext.commands import Context
from configs.words_lookup import blacklist_words, trigger_words


class ContextMixin:
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
        return any(word in word_list for word in self.tokens)

    @property
    def is_reward_redemption(self):
        return "custom-reward-id" in self.message.tags


class AdvancedContext(ContextMixin, Context):
    pass

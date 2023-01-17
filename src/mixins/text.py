from emoji import is_emoji


class TextProcessMixin:
    """
    Mixin to tokenize a chat message and count occurrence
    of mentions, emotes and emojis in the message
    """

    _emotes = None

    def _count_emojis(self, message):
        """
        Tokenize the chat message and returns a dictionary which
        keys are emojis and valuse are count of occurrence for
        each emoji in the chat message
        """
        emojis = [word for word in message.split(" ") if is_emoji(word)]
        return {emoji: emojis.count(emoji) for emoji in set(emojis)}

    def _count_emotes(self, message):
        """
        Tokenize the chat message and returns a dictionary which
        keys are emotes and valuse are count of occurrence for
        each emote in the chat message
        """
        emotes = [word for word in message.split(" ") if word in self._emotes]
        return {emote: emotes.count(emote) for emote in set(emotes)}

    def _count_mentions(self, message):
        """
        Tokenize the chat message and returns a dictionary which
        keys are mentions and valuse are count of occurrence for
        each mention in the chat message
        """
        mentions = [
            word.replace(",", "") for word in message.split(" ") if word.startswith("@")
        ]
        return {mention: mentions.count(mention) for mention in set(mentions)}

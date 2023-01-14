from configs.words_lookup import blacklist_words, trigger_words


class ChatMessage:
    def __init__(self, message):
        self.content = message

    def tokens(self):
        return self.content.split(" ")

    def has_forbidden_word(self):
        return self._check_words_in(blacklist_words)

    def has_trigger_word(self):
        return self._check_words_in(trigger_words)

    def _check_words_in(self, word_list):
        for word in self.tokens():
            if word in word_list:
                return True

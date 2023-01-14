from src.moderator import Moderator
from src.crawler import Crawler


class ExeCommandLine:
    def __init__(self, args):
        self._bot_class = self._select_class(args)

    def _parse_args(self, args: list):
        if len(args) >= 3:
            raise ValueError(
                "Too many Arguments: Accepted arguments are: crawl or moderate"
            )

        if len(args) == 1:
            return "crawl"

        return args[1].lower()

    def _validate_class(self, arg):
        if arg not in ["crawl", "moderate"]:
            raise ValueError(
                "Invalid Arguments: Accepted arguments are: crawl or moderate"
            )

    def _select_class(self, args):
        choosen_bot = self._parse_args(args)
        self._validate_class(choosen_bot)
        bot_classes = {"crawl": Crawler, "moderate": Moderator}
        return bot_classes[choosen_bot]

    def create_bot(self):
        new_bot = self._bot_class()
        print(f"Created a bot with type < {new_bot.__class__.__name__} >")
        return new_bot

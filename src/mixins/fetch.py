import os
import requests


class FetchApiMixin:
    """
    Mixin to call api and list global and channel emotes
    """

    _emotes_providers = ["twitch", "7tv", "bttv", "ffz"]
    _channel_emotes_endpoint = f"https://emotes.adamcy.pl/v1/channel/{os.environ['CHANNEL']}/emotes/twitch.7tv.bttv.ffz"
    _global_emotes_endpoint = (
        "https://emotes.adamcy.pl/v1/global/emotes/twitch.7tv.bttv.ffz"
    )

    def _fetch_emotes(self):
        """
        Calls api to get list of channel and global emotes
        """
        self._get_emotes(self._global_emotes_endpoint, "global")
        self._get_emotes(self._channel_emotes_endpoint, "channel")

    def _get_emotes(self, url, set):
        response = requests.get(url)
        emotes_json = response.json()
        setattr(self, f"_{set}_emotes", emotes_json)

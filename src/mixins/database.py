import os
import psycopg2
import requests


class DataBaseProcessMixin:
    _conn_string = os.environ["DB_URL"]
    _providers = ["twitch", "7tv", "bttv", "ffz"]
    _channel_emotes_endpoint = f"https://emotes.adamcy.pl/v1/channel/{os.environ['CHANNEL']}/emotes/twitch.7tv.bttv.ffz"
    _global_emotes_endpoint = (
        "https://emotes.adamcy.pl/v1/global/emotes/twitch.7tv.bttv.ffz"
    )

    def connect_database(func):
        def wrapper(*args, **kwargs):
            self = args[0]
            conn = psycopg2.connect(self._conn_string)
            cursor = conn.cursor()
            kwargs["cursor"] = cursor
            func(*args, **kwargs)
            conn.commit()
            cursor.close()
            conn.close()

        return wrapper

    async def init_database_routine(self):
        self._create_emotes_table()
        self._create_messages_table()
        self._update_emotes()

    def _update_emotes(self):
        print("Updating global emote database")
        self._get_emotes(self._global_emotes_endpoint, "global")
        print("Updating channel emote database")
        self._get_emotes(self._channel_emotes_endpoint, "channel")

    def _get_emotes(self, url, set):
        response = requests.get(url)
        data = response.json()
        for emote in data:
            self._insert_into_emotes(emote, set)

    @connect_database
    def _insert_into_emotes(self, emote, set, cursor):
        exist_query = """select exists
                        (select code from emotes where code=%s);"""
        cursor.execute(exist_query, (emote["code"],))

        if not cursor.fetchone():
            insert_query = """insert into emotes
                            (code, url, provider, set)
                            values (%s, %s, %s, %s);"""
            cursor.execute(
                insert_query,
                (
                    emote["code"],
                    emote["urls"][0]["url"],
                    self._providers[emote["provider"]],
                    set,
                ),
            )
            print(f"New emote added: {emote['code']}")

    @connect_database
    def insert_into_messages(self, user, message, cursor):
        insert_query = """insert into chat_messages
                        (username, message)
                        values (%s, %s);"""
        cursor.execute(
            insert_query,
            (
                user,
                message,
            ),
        )

    @connect_database
    def _create_messages_table(self, cursor):
        cursor.execute(
            """create table if not exists chat_messages(
            id serial primary key,
            username varchar(255),
            message text,
            date timestamp default current_date)"""
        )

    @connect_database
    def _create_emotes_table(self, cursor):
        cursor.execute(
            """create table if not exists emotes(
            id serial primary key,
            code varchar(255),
            url varchar(255),
            provider varchar(255),
            set varchar(255),
            date timestamp default current_date)"""
        )

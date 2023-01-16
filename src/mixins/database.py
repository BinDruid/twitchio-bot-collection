import os
import emoji
import psycopg2
import requests


class DataBaseProcessMixin:
    _emotes = None
    _conn_string = os.environ["DB_URL"]
    _emotes_providers = ["twitch", "7tv", "bttv", "ffz"]
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
        self._create_chats_table()
        self._create_emotes_table()
        self._create_message_emojis_table()
        self._create_message_emotes_table()
        self._create_message_mentions_table()
        self._update_emotes()
        self._make_emote_list()

    def _update_emotes(self):
        print("Updating database for global emotes")
        self._fetch_emotes(self._global_emotes_endpoint, "global")
        print("Updating database for channel emotes")
        self._fetch_emotes(self._channel_emotes_endpoint, "channel")

    def _fetch_emotes(self, url, set):
        response = requests.get(url)
        data = response.json()
        for emote in data:
            self._insert_into_emotes_table(emote, set)

    @connect_database
    def _insert_into_emotes_table(self, emote, set, cursor):
        exist_query = """select exists
                        (select code from emotes where code=%s);"""
        cursor.execute(exist_query, (emote["code"],))
        emote_exists = cursor.fetchone()[0]
        if not emote_exists:
            insert_query = """insert into emotes
                            (code, url, provider, set)
                            values (%s, %s, %s, %s);"""
            cursor.execute(
                insert_query,
                (
                    emote["code"],
                    emote["urls"][0]["url"],
                    self._emotes_providers[emote["provider"]],
                    set,
                ),
            )
            print(f"New emote added: {emote['code']}")

    @connect_database
    def insert_into_chats_table(self, context, cursor):
        message = context.message.content
        author = context.author
        emotes_count = self._count_emotes(message)
        emojis_count = self._count_emojis(message)
        mentions_count = self._count_mentions(message)
        insert_query = """insert into chats
                        (message, username, user_id, is_sub, is_mod, is_vip)
                        values (%s, %s, %s, %s, %s, %s) returning id;"""
        cursor.execute(
            insert_query,
            (
                message,
                author.name,
                author.id,
                author.is_subscriber,
                author.is_mod,
                author.is_vip,
            ),
        )
        message_id = cursor.fetchone()[0]
        emote_insert_query = """insert into message_emotes
                            (message_id, emote_id, count)
                            values (%s, %s, %s);"""
        for emote in emotes_count:
            cursor.execute(
                emote_insert_query,
                (message_id, self._emotes[emote], emotes_count[emote]),
            )
        emoji_insert_query = """insert into message_emojis
                            (message_id, emoji, count)
                            values (%s, %s, %s);"""
        for emj in emojis_count:
            cursor.execute(
                emoji_insert_query,
                (message_id, emj, emojis_count[emj]),
            )

        mention_insert_query = """insert into message_mentions
                            (message_id, mention, count)
                            values (%s, %s, %s);"""
        for mention in mentions_count:
            cursor.execute(
                mention_insert_query,
                (message_id, mention, mentions_count[mention]),
            )

    @connect_database
    def _create_chats_table(self, cursor):
        cursor.execute(
            """create table if not exists chats(
            id serial primary key,
            message varchar(600),
            username varchar(255),
            user_id integer,
            is_sub boolean default false,
            is_mod boolean default false,
            is_vip boolean default false,
            date timestamptz default (now() at time zone 'Iran'))"""
        )

    @connect_database
    def _create_message_mentions_table(self, cursor):
        cursor.execute(
            """create table if not exists message_mentions(
            id serial primary key,
            message_id integer references chats(id) not null,
            mention varchar(255),
            count integer)"""
        )

    @connect_database
    def _create_message_emojis_table(self, cursor):
        cursor.execute(
            """create table if not exists message_emojis(
            id serial primary key,
            message_id integer references chats(id) not null,
            emoji varchar(255),
            count integer)"""
        )

    @connect_database
    def _create_message_emotes_table(self, cursor):
        cursor.execute(
            """create table if not exists message_emotes(
            id serial primary key,
            message_id integer references chats(id) not null,
            emote_id integer references emotes(id) not null,
            count integer)"""
        )

    @connect_database
    def _create_emotes_table(self, cursor):
        cursor.execute(
            """create table if not exists emotes(
            id serial primary key,
            code varchar(255),
            url varchar(255),
            provider varchar(10),
            set varchar(10),
            date timestamptz default (now() at time zone 'Iran'))"""
        )

    @connect_database
    def _make_emote_list(self, cursor):
        cursor.execute("""select id, code from emotes;""")
        emotes = cursor.fetchall()
        # emote[1] is emote code
        # emote[0] is id of the emote
        self._emotes = {emote[1]: emote[0] for emote in emotes}

    def _count_emojis(self, message):
        emojis = [word for word in message.split(" ") if emoji.is_emoji(word)]
        return {emj: emojis.count(emj) for emj in set(emojis)}

    def _count_emotes(self, message):
        emotes = [word for word in message.split(" ") if word in self._emotes]
        return {emote: emotes.count(emote) for emote in set(emotes)}

    def _count_mentions(self, message):
        mentions = [
            word.replace(",", "") for word in message.split(" ") if word.startswith("@")
        ]
        return {mention: mentions.count(mention) for mention in set(mentions)}

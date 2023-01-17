import os
import psycopg2
from .text import TextProcessMixin
from .fetch import FetchApiMixin
from datetime import datetime


class DataBaseProcessMixin(FetchApiMixin, TextProcessMixin):
    """
    Mixin to handle database operations including
    creating initial tables, consuming emotes api and then
    updating and inserting new emotes and chat messages
    """

    emotes_ready = False
    _conn_string = os.environ["DB_URL"]

    def connect_database(func):
        """
        A decorator which wraps any database query excution with
        a creat, commit and close connection operation. Also passes
        a cursor to wrapped method.
        """

        def wrapper(*args, **kwargs):
            self = args[0]
            conn = psycopg2.connect(self._conn_string)
            cursor = conn.cursor()
            kwargs["cursor"] = cursor
            func(*args, **kwargs)
            conn.commit()
            cursor.close()

        return wrapper

    async def init_database_routine(self):
        self._fetch_emotes()
        self._update_emotes()
        self._make_emote_list()

    def _update_emotes(self):
        """
        Checks if a new emote (either global or channel) has been added to channel
        In that case the emote will get inserted to emotes tabale
        """
        print("Updating database for global emotes")
        for emote in self._global_emtoes:
            self._insert_into_emotes_table(emote, "global")
        print("Updating database for channel emotes")
        for emote in self._channel_emtoes:
            self._insert_into_emotes_table(emote, "channel")

    @connect_database
    def _insert_into_emotes_table(self, emote, set, cursor):
        exist_query = """select exists
                        (select code from emotes where code=%s);"""
        cursor.execute(exist_query, (emote["code"],))
        emote_exists = cursor.fetchone()[0]
        if not emote_exists:
            insert_query = """insert into emotes
                            (code, url, provider, set, date)
                            values (%s, %s, %s, %s, %s);"""
            cursor.execute(
                insert_query,
                (
                    emote["code"],
                    emote["urls"][0]["url"],
                    self._emotes_providers[emote["provider"]],
                    set,
                    datetime.now(),
                ),
            )
            print(f"New emote added: {emote['code']}")

    @connect_database
    def insert_into_chats_table(self, message, author, cursor):
        insert_query = """insert into chats
                        (message, username, user_id, is_sub, is_mod, is_vip, date)
                        values (%s, %s, %s, %s, %s, %s, %s) returning id;"""
        cursor.execute(
            insert_query,
            (
                message,
                author.name,
                author.id,
                author.is_subscriber,
                author.is_mod,
                author.is_vip,
                datetime.now(),
            ),
        )
        message_id = cursor.fetchone()[0]

        emotes_count = self._count_emotes(message)
        self._insert_into_message_emotes(emotes_count, message_id, cursor)

        mentions_count = self._count_mentions(message)
        self._insert_into_message_mentions(mentions_count, message_id, cursor)

        emojis_count = self._count_emojis(message)
        self._insert_into_message_emojis(emojis_count, message_id, cursor)

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
        """
        Creats a dictionary from all emotes in database which
        keys are representing emote code and value is id of the emote
        """
        cursor.execute("""select id, code from emotes;""")
        emotes = cursor.fetchall()
        # emote[1] is refrencing to code column in emotes table
        # emote[0] is refrencing to id column in emotes table
        self._emotes = {emote[1]: emote[0] for emote in emotes}
        self.emotes_ready = True

    def _insert_into_message_emotes(self, emotes_count, message_id, cursor):
        insert_query = """insert into message_emotes
                            (message_id, emote_id, count)
                            values (%s, %s, %s);"""
        for emote in emotes_count:
            cursor.execute(
                insert_query,
                (message_id, self._emotes[emote], emotes_count[emote]),
            )

    def _insert_into_message_emojis(self, emojis_count, message_id, cursor):
        insert_query = """insert into message_emojis
                            (message_id, emoji, count)
                            values (%s, %s, %s);"""
        for emoji in emojis_count:
            cursor.execute(
                insert_query,
                (message_id, emoji, emojis_count[emoji]),
            )

    def _insert_into_message_mentions(self, mentions_count, message_id, cursor):
        insert_query = """insert into message_mentions
                            (message_id, mention, count)
                            values (%s, %s, %s);"""
        for mention in mentions_count:
            cursor.execute(
                insert_query,
                (message_id, mention, mentions_count[mention]),
            )

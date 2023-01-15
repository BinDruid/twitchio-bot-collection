import os
import psycopg2
import requests


class DataBaseProcessMixin:
    conn_string = os.environ["DB_URL"]
    providers = ["twitch", "7tv", "bttv", "ffz"]
    channel_url = f"https://emotes.adamcy.pl/v1/channel/{os.environ['CHANNEL']}/emotes/twitch.7tv.bttv.ffz"
    global_url = f"https://emotes.adamcy.pl/v1/global/emotes/twitch.7tv.bttv.ffz"

    def init_database_routine(self):
        self._create_emotes_table()
        self._create_messages_table()
        self._update_emotes()

    def _update_emotes(self):
        print("Updating global emote database")
        self._get_emotes(self.global_url, "global")
        print("Updating channel emote database")
        self._get_emotes(self.channel_url, "channel")

    def _get_emotes(self, url, set):
        response = requests.get(url)
        data = response.json()
        for emote in data:
            self._insert_into_emotes(emote, set)

    def _insert_into_emotes(self, emote, set):
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
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
                    self.providers[emote["provider"]],
                    set,
                ),
            )
            print(f"New emote added: {emote['code']}")

        conn.commit()
        cursor.close()

    def insert_into_messages(self, user, message):
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()
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

        conn.commit()
        cursor.close()

    def _create_messages_table(self):
        conn = psycopg2.connect(self.conn_string)
        cursor = conn.cursor()

        cursor.execute(
            """create table if not exists chat_messages(
            id serial primary key,
            username varchar(255),
            message text,
            date timestamp default current_date)"""
        )

        conn.commit()
        cursor.close()

    def _create_emotes_table(self):
        conn_string = os.environ["DB_URL"]
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        cursor.execute(
            """create table if not exists emotes(
            id serial primary key,
            code varchar(255),
            url varchar(255),
            provider varchar(255),
            set varchar(255),
            date timestamp default current_date)"""
        )

        conn.commit()
        cursor.close()

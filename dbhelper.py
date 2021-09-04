from random import sample
import sqlite3

from settings import DATABASE_NAME

class DBHelper:
    def __init__(self, dbname=DATABASE_NAME):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cur = self.conn.cursor()

    def setup(self):
        group_table = '''CREATE TABLE IF NOT EXISTS group_table(
                    chat_id INTEGER PRIMARY KEY,
                    group_name VARCHAR(100),
                    group_proc VARCHAR(1)
                    )'''
        user_table = '''CREATE TABLE IF NOT EXISTS user_table(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    user_neme VARCHAR(100)
                    )'''
        self.cur.execute(group_table)
        self.cur.execute(user_table)
        self.conn.commit()

    def add_group(self, id, name):
        stmt = '''INSERT INTO group_table(chat_id, group_name, group_proc)
                VALUES("{}","{}",{})'''
        stmt = stmt.format(id, name, '0')
        self.cur.execute(stmt)
        self.conn.commit()

    def check_group(self, id):
        stmt = 'SELECT * FROM group_table WHERE chat_id={}'
        stmt = stmt.format(id)
        self.cur.execute(stmt)
        return len(self.cur.fetchall())

    def check_game(self, id):
        stmt = 'SELECT * FROM group_table WHERE chat_id={}'
        stmt = stmt.format(id)
        self.cur.execute(stmt)
        return int(self.cur.fetchone()[2])

    def start_game(self, id):
        stmt = 'UPDATE group_table SET group_proc=1 WHERE chat_id = "{}"'
        stmt = stmt.format(id)
        self.cur.execute(stmt)
        self.conn.commit()

    def end_game(self, id):
        stmt = 'UPDATE group_table SET group_proc=0 WHERE chat_id = "{}"'
        stmt = stmt.format(id)
        self.cur.execute(stmt)
        self.conn.commit()

    def add_player(self, chat_id, user_id, user_neme):
        stmt = '''INSERT INTO user_table(chat_id, user_id, user_neme)
                VALUES("{}","{}","{}")'''
        stmt = stmt.format(chat_id, user_id, user_neme)
        self.cur.execute(stmt)
        self.conn.commit()

    def check_player(self, chat_id, user_id):
        stmt = 'SELECT * FROM user_table WHERE chat_id={} and user_id={}'
        stmt = stmt.format(chat_id, user_id)
        self.cur.execute(stmt)
        return len(self.cur.fetchall())

    def count_player(self, chat_id):
        stmt = 'SELECT * FROM user_table WHERE chat_id={}'
        stmt = stmt.format(chat_id)
        self.cur.execute(stmt)
        return len(self.cur.fetchall())

    def delete_all(self, chat_id):
        stmt = 'DELETE FROM user_table WHERE chat_id={}'
        stmt = stmt.format(chat_id)
        self.cur.execute(stmt)
        return len(self.cur.fetchall())

    def get_player(self, chat_id):
        stmt = 'SELECT * FROM user_table WHERE chat_id={}'
        stmt = stmt.format(chat_id)
        self.cur.execute(stmt)
        players = self.cur.fetchall()
        return sample(players, 2)

    def get_all_players(self, chat_id):
        stmt = 'SELECT * FROM user_table WHERE chat_id={}'
        stmt = stmt.format(chat_id)
        self.cur.execute(stmt)
        players = self.cur.fetchall()
        return players

    def delete_player(self, user_id, chat_id):
        stmt = 'DELETE FROM user_table WHERE chat_id={} and user_id={}'
        stmt = stmt.format(chat_id, user_id)
        self.cur.execute(stmt)

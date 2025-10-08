import sqlite3


class DataBase:
    def __init__(self, path: str):
        self.path = path

    def init_db(self):
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS playlists
                                (weekid INTEGER, topic TEXT, name TEXT, link TEXT, altText TEXT)''')
            conn.commit()

    def add_music(self, name, link, topic, alt, weekid):
        print("Connecting ...")
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO playlists VALUES (?, ?, ?, ?, ?)""",
                        (weekid, topic, name, link, alt))
            conn.commit()
        print("Done ...")

    def create_playlist(self):
        pass

    def show_playlist(self):
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute('''SELECT * FROM playlists''')
            return cur.fetchall()

    def get_list_of_week(self, week):
        # Validtion for week input.
        try:
            week_int = int(week)
        except (ValueError, TypeError):
            raise ValueError("The week must be integer")

        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute('''SELECT * FROM playlists WHERE weekid= ? ''', (week_int,))
            return cur.fetchall()

    def remove_music(self):
        pass

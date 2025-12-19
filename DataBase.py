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
    
    def add_custom_text(self, text, weekid):
        print("Connecting ...")
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO custom_text (text, week_id) VALUES (?, ?)""",
                        (text, weekid))
            conn.commit()
        print("Done ...")
        return f"{text} added to {weekid}th weekly music"

    def get_custom_text(self, weekid):
        print("Connecting for getting custom text...")
        with sqlite3.connect(self.path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT text FROM custom_text WHERE week_id = ?",
                        (weekid,))
            rows = cur.fetchall()
            texts = [row[0] for row in rows]
            conn.commit()
        print("Done ...")
        return texts
        
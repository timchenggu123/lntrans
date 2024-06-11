import sqlite3

class NarouDB:
    def connect(self):
        self.conn = sqlite3.connect("narou")
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

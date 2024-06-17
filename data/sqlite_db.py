import sqlite3
import pandas
class NarouDB:
    TABLE_NOVELS_META_RAW = "novels_meta_raw"
    
    def connect(self):
        self.conn = sqlite3.connect("narou")
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor
    
    def update_novels_meta_raw(self, df: pandas.DataFrame):
        df.to_sql(self.TABLE_NOVELS_META_RAW, self.conn, if_exists="replace")

    def get_ncodes(self,lim=10, offset=0):
        self.cursor.execute(f"SELECT ncode FROM {self.TABLE_NOVELS_META_RAW} LIMIT {lim} OFFSET {offset}")
        return map(lambda x: x[0], self.cursor.fetchall())
    
    def get_novel_name(self, ncode):
        ncode=ncode.upper()
        self.cursor.execute(f"SELECT title FROM {self.TABLE_NOVELS_META_RAW} WHERE ncode=?", (ncode,))
        return self.cursor.fetchone()[0]
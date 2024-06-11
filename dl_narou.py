from crawlers import NcodeCrawler
from api import narou
from data import NarouDB
import os

def main():
    # Connect to DB
    db = NarouDB()
    conn, cur = db.connect()

    # Update the metadata
    # TODO: implement a better way to check if the data is updated
    do_update = False
    if do_update:
        df = narou.get_novels_ranked(top=10)
        df.to_sql("novels_raw", conn, if_exists="replace")

    cur.execute("SELECT ncode FROM novels_raw")
    res = cur.fetchall()
    
    # Download the novels
    output_dir = "raw/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    ncode_list = [res[i][0] for i in range(len(res))]
    crawler = NcodeCrawler(output_dir=output_dir)
    for ncode in ncode_list:
        crawler.queue_novel(ncode, s_chptr=1, e_chptr=1)
    crawler.run()

if __name__ == "__main__":
    main()
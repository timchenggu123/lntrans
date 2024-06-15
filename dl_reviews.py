from crawlers.ncode import NcodeReviewsCrawler
from api import narou
from data import NarouDB
from db_updater import update_top_100_novels
import os

def main():
    # Connect to DB
    db = NarouDB()
    db.connect()

    # Make the output directory if doesn't exists
    output_dir = "raw/reviews/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the novel codes
    ncode_list = db.get_ncodes(lim=20, offset=36)  
    crawler = NcodeReviewsCrawler(output_dir=output_dir)
    for ncode in ncode_list:
        crawler.add(ncode)
    crawler.run()

if __name__ == "__main__":
    main()
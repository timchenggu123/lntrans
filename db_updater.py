from data import NarouDB
from api import narou as api

def update_top_100_novels():
    # Connect to DB
    db = NarouDB()

    # Update the metadata
    # TODO: implement a better way to check if the data is updated
    df = api.get_novels_ranked(top=100)
    db.update_novels_meta_raw(df)

def update_newest_novels():
    # Connect to DB
    db = NarouDB()

    df = api.get_novels_newest(top=100)
    db.update_novels_meta_raw(df)
    

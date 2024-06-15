import requests
import pandas as pd
URL = "https://api.syosetu.com/novelapi/api/"

def get_novels_ranked(top=100) -> pd.DataFrame:
    '''
    Get the top novels from Narou
    Returns a DataFrame with the top novels' meta data

    Parameters:
    top (int): The number of novels to get. Value must be between 1 and 100
    '''
    response = requests.get(URL, params={"out": "json", "lim": top, "order": "hyoka"})
    response = response.json()[1:]
    df = pd.json_normalize(response)
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df["novelupdated_at"] = pd.to_datetime(df["novelupdated_at"])
    return df

def get_novels_newest(top=100) -> pd.DataFrame:
    '''
    Get the newest novels from Narou
    Returns a DataFrame with the newest novels' meta data
    '''
    response = requests.get(URL, params={"out": "json", "lim": top, "order": "new"})
    response = response.json()[1:]
    df = pd.json_normalize(response)
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df["novelupdated_at"] = pd.to_datetime(df["novelupdated_at"])
    return df

if __name__ == "__main__":
    df = get_novels_ranked()
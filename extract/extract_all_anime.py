import requests
import json
import time
import os


def extract_all_anime():
    #create folder if not exists
    os.makedirs("data/raw",exist_ok=True)

    page=1000
    has_next_page=True

    while has_next_page and page <1200:
        try:

            url=f"https://api.jikan.moe/v4/anime?page={page}"

            response=requests.get(url)
            response.raise_for_status()
            data=response.json()

            #save raw json page 
            file_path=f"data/raw/anime_page_{page}.json"

            with open(file_path,"w",encoding="utf-8") as file:
                json.dump(data,file,indent=4)

            print(f"Saved page {page}")

            #check next page
            has_next_page=data["pagination"]["has_next_page"]

            page+=1

            #avoid rate limit
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error on page {page}:{e}")
            
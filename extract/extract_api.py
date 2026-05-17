import requests
import pandas as pd

def extract_top_anime():
    url= "https://api.jikan.moe/v4/top/anime"

    response=requests.get(url)
    data=response.json()

    anime_list=[]

    for anime in data['data']:

        genres_name=[genre["name"] for genre in anime["genres"]]
        # english_title=None
        # default_title=None

        # for t in anime["titles"]:
        #     if t["type"]=="English":
        #         english_title=t["title"]
        #     if t ["type"]=="Default":
        #         default_title=t["title"]

        # Use English title if available
        # Otherwise use Default Title
        #final_title=english_title if english_title else default_title
        english_title=anime["title_english"]
        default_title=anime["title"]
        final_title=english_title if english_title else default_title
        

        
 
        anime_list.append({
            "title":final_title,
            "episodes":anime["episodes"],
            "status":anime["status"],
            "aired":anime["aired"].get("string"),
            "duration":anime["duration"],
            "rating":anime["rating"],
            "score":anime["score"],
            "scored_by":anime["scored_by"],
            "popularity":anime["popularity"],
            "members":anime["members"],
            "favorites":anime["favorites"],
            "studios":anime["studios"].get("name"),
            "genres":", ".join(genres_name)
        })
    df=pd.DataFrame(anime_list)

    return df

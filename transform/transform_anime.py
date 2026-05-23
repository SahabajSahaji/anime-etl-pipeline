import json
import pandas as pd
from pathlib import Path

raw_dir=Path("data/raw")

processed_dir=Path("data/processed")

processed_dir.mkdir(
    parents=True,
    exist_ok=True
)

output_file=processed_dir/"anime_clean.csv"

anime_list=[]

for json_file in raw_dir.glob("*.json"):
    print(f"Reading {json_file.name}")

    with open(json_file,"r",encoding="utf-8") as f:
        data=json.load(f)
    
    #Get anime list
    for anime in data.get("data",[]):
        #Genres
        genres_name=[
            genre["name"]
            for genre in anime.get("genres",[])
        ]
        
        #English title fallback
        english_title=anime.get("title_english")
        default_title=anime.get("title")

        final_title={
            english_title
            if english_title
            else default_title
        }

        #Append cleaned data

        anime_list.append({

            "mal_id": anime.get("mal_id"),

            "title": final_title,

            "episodes": anime.get("episodes"),

            "status": anime.get("status"),

            "aired": anime.get("aired",{}).get("string"),

            "duration": anime.get("duration"),

            "rating": anime.get("rating"),

            "score": anime.get("score"),

            "scored_by": anime.get("scored_by"),

            "MyAnimeList_Rank": anime.get("rank")

            "popularity": anime.get("popularity"),

            "members": anime.get("members"),

            "favorites": anime.get("favorites"),

            "year": anime.get("year"),

            "season": anime.get("season"),

            "studios": ", ".join(
                studio["name"]
                for studio in anime.get("studios",[])
            ),

            "genres": ", ".join(genres_name)

        })

# Create DataFrame

df=pd.DataFrame(anime_list)

#Remove duplicates

df.drop_duplicates(
    subset=["mal_id"],
    inplace=True
)


# Create processed folder


df.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print("\nTransformation complete")
print(f"Total Anime: {len(df)}")
print(f"Saved: {output_file}")
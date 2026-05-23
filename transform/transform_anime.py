import json
import pandas as pd
from pathlib import Path

raw_dir=Path("data/raw")

processed_dir=Path("data/processed")

processed_dir.mkdir(parents=True,exist_ok=True)

log_dir=Path("logs")

log_dir.mkdir(parents=True,exist_ok=True)

output_file=processed_dir/"anime_clean.csv"

checkpoint_file=log_dir / "processed_file.txt"

error_log=log_dir / "error_log.txt"

#Load Processed Files

processed_files=set()

if checkpoint_file.exists():

    with open(checkpoint_file,"r",encoding="utf-8") as f:
        processed_files=set(line.strip() for line in f)

csv_exists =output_file.exists()

json_files =sorted(raw_dir.glob("*.json"))

for json_file in json_files:

    # Skip already processed files
    if json_file.name in processed_files:

        print(f"Skipping {json_file.name}")
        continue

    try:

        print(f"Processing {json_file.name}")

        # Read JSON
        with open(json_file,"r",encoding="utf-8") as f:

            data = json.load(f)

        anime_list = []


        for anime in data.get("data", []):

            genres_name = [genre["name"]for genre in anime.get("genres",[])]

            english_title = anime.get("title_english")

            default_title = anime.get("title")

            final_title = (english_title if english_title else default_title)

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

                "MyAnimeList_Rank": anime.get("rank"),

                "popularity": anime.get("popularity"),

                "members": anime.get("members"),

                "favorites": anime.get("favorites"),

                "year": anime.get("year"),

                "season": anime.get("season"),

                "studios": ", ".join(studio["name"]for studio in anime.get("studios",[])),

                "genres": ", ".join(genres_name)

            })

        # Create DataFrame

        df=pd.DataFrame(anime_list)

        #Remove duplicates

        df.drop_duplicates(subset=["mal_id"],inplace=True)



        #if we didn't mention mode as a it will automatically use mode "w"for this every json page data override over and over till the last json file
        #so we only get the last json file as here we need to mention mode as "a"
        df.to_csv(output_file,mode="a",header=not csv_exists,index=False,encoding="utf-8")

        #CSV now exists

        csv_exists= True

        #Save CheckPoint

        with open (checkpoint_file,"a",encoding="utf-8") as f:
            f.write(json_file.name + "\n")

    except Exception as e:

        print(f"Error in {json_file.name}")

        print(e)

        #Save error log
        with open(error_log,"a",encoding="utf-8") as log:
            log.write(f"{json_file.name}-> {e}\n")
            
final_df = pd.read_csv(output_file)

print("\nTransformation complete")
print(f"Total Anime: {len(final_df)}")
print(f"Saved: {output_file}")
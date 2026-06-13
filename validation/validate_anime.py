import json
import pandas as pd
from pathlib import Path


raw_dir = Path("data/raw")

report_dir = Path("reports")
report_dir.mkdir(
    parents=True,
    exist_ok=True
)

report_file = report_dir / "data_quality_report.txt"

invalid_records_file = (
    report_dir / "invalid_records.csv"
)


total_anime = 0

missing_titles = 0
missing_scores = 0
missing_genres = 0
missing_studios = 0
missing_year = 0
missing_popularity = 0

invalid_scores = 0
invalid_episodes = 0

duplicate_ids = 0


seen_ids = set()

invalid_records = []



json_files = sorted(
    raw_dir.glob("*.json")
)

for json_file in json_files:

    print(f"Validating {json_file.name}")

    with open(
        json_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    for anime in data.get("data", []):

        total_anime += 1

        mal_id = anime.get("mal_id")



        if mal_id in seen_ids:

            duplicate_ids += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Duplicate MAL ID"
            })

        else:
            seen_ids.add(mal_id)


        if not anime.get("title"):

            missing_titles += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Title"
            })


        score = anime.get("score")

        if score is None:

            missing_scores += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Score"
            })

        elif not (0 <= score <= 10):

            invalid_scores += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Invalid Score"
            })



        episodes = anime.get("episodes")

        if (
            episodes is not None
            and episodes < 0
        ):

            invalid_episodes += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Invalid Episodes"
            })

  

        if not anime.get("genres"):

            missing_genres += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Genres"
            })


        if not anime.get("studios"):

            missing_studios += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Studios"
            })


        if anime.get("year") is None:

            missing_year += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Year"
            })


        if anime.get("popularity") is None:

            missing_popularity += 1

            invalid_records.append({
                "mal_id": mal_id,
                "title": anime.get("title"),
                "issue": "Missing Popularity"
            })



total_issues = (
    missing_titles
    + missing_scores
    + missing_genres
    + missing_studios
    + missing_year
    + missing_popularity
    + invalid_scores
    + invalid_episodes
    + duplicate_ids
)

quality_score = (
    ((total_anime - total_issues) / total_anime)
    * 100
)



invalid_df = pd.DataFrame(
    invalid_records
)

invalid_df.to_csv(
    invalid_records_file,
    index=False,
    encoding="utf-8"
)



with open(
    report_file,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "===== DATA QUALITY REPORT =====\n\n"
    )

    report.write(
        f"Total Anime: {total_anime}\n\n"
    )

    report.write(
        f"Missing Titles: {missing_titles}\n"
    )

    report.write(
        f"Missing Scores: {missing_scores}\n"
    )

    report.write(
        f"Missing Genres: {missing_genres}\n"
    )

    report.write(
        f"Missing Studios: {missing_studios}\n"
    )

    report.write(
        f"Missing Year: {missing_year}\n"
    )

    report.write(
        f"Missing Popularity: {missing_popularity}\n"
    )

    report.write(
        f"Invalid Scores: {invalid_scores}\n"
    )

    report.write(
        f"Invalid Episodes: {invalid_episodes}\n"
    )

    report.write(
        f"Duplicate MAL IDs: {duplicate_ids}\n\n"
    )

    report.write(
        f"Total Issues: {total_issues}\n\n"
    )

    report.write(
        f"Data Quality Score: "
        f"{quality_score:.2f}%\n"
    )


print("\nValidation Complete")
print(f"Total Anime: {total_anime}")
print(f"Total Issues: {total_issues}")
print(f"Data Quality Score: {quality_score:.2f}%")
print(f"Report: {report_file}")
print(f"Invalid Records: {invalid_records_file}")
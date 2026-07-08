import sqlite3
import pandas as pd
from config import DATABASE_FILE


conn=sqlite3.connect(DATABASE_FILE)

print("Connect to database")

#Top rated:--

top_rated_query="""
SELECT
    title,
    score,
    scored_by
FROM anime
WHERE score IS NOT NULL
ORDER BY score DESC
LIMIT 10;
"""

top_rated=pd.read_sql(top_rated_query,conn)

print("\n TOP RATED ANIME RANKING:--")
print(top_rated)

#Most Popular:--

most_popular_query="""
SELECT
    title,
    popularity,
    members
FROM anime
ORDER BY popularity ASC
LIMIT 10;
"""

most_popular=pd.read_sql(most_popular_query,conn)

print("\n MOST POPULAR ANIME RANKING:--")
print(most_popular)

#Most Loved Anime:--

most_loved_query="""
SELECT
    title,
    favorites
FROM anime
ORDER BY favorites DESC
LIMIT 10;
"""

most_loved=pd.read_sql(most_loved_query,conn)

print("\n MOST LOVED ANIME RANKING:---")
print(most_loved)

#Best Anime Studios:---

best_anime_studios_query="""
SELECT
    studios,
    AVG(score) AS avg_score,
    COUNT(*) AS total_anime
FROM anime
WHERE score IS NOT NULL
GROUP BY studios
HAVING total_anime > 5
ORDER BY avg_score DESC;
"""

best_anime_studios=pd.read_sql(best_anime_studios_query,conn)

print("\n Best Anime Studio Ranking:--")
print(best_anime_studios)

#Seasonal Trends:--

seasonal_trends_query="""
SELECT
    season,
    AVG(score) AS avg_score,
    COUNT(*) AS anime_count
FROM anime
WHERE score IS NOT NULL
GROUP BY season;
"""

seasonal_trends=pd.read_sql(seasonal_trends_query,conn)

print("\n Seasonal Trends:---")
print(seasonal_trends)

#Hidden Gem Detector:--
#Find anime with  high score and low popularity
#Formula: Hidden_Gem=(score*favorites)/popularity

hidden_gem_query="""
SELECT
    title,
    score,
    favorites,
    popularity,
    ROUND(
        (score * favorites * 1.0 / popularity),
        2
    ) AS hidden_gem_score
FROM anime
WHERE score IS NOT NULL
AND popularity > 0
ORDER BY hidden_gem_score DESC
LIMIT 20;
"""

hidden_gem=pd.read_sql(hidden_gem_query,conn)

print("\n Hidden Gems:---")
print(hidden_gem)

#Fan Loyalty:---
#high ratio means: strong random , cult following
#Formula Fan_Loyalty =favorites/members

fan_loyalty_query="""
SELECT
    title,
    favorites,
    members,
    ROUND(
        (favorites * 1.0 / members),
        4
    ) AS fan_loyalty
FROM anime
WHERE members > 10000
ORDER BY fan_loyalty DESC
LIMIT 20;
"""

fan_loyalty=pd.read_sql(fan_loyalty_query,conn)

print("\n Fan Loyalty Ranking:---")
print(fan_loyalty)

#Overhyped Anime Detector:---
#Anime with massive popularity , relatively lower score
#Formula: Overhype=members/score

overhyped_anime_detector_query="""
SELECT
    title,
    score,
    members,
    ROUND(
        (members * 1.0 / score),
        2
    ) AS overhype_score
FROM anime
WHERE score IS NOT NULL
ORDER BY overhype_score DESC
LIMIT 20;
"""

overhyped_anime_detector=pd.read_sql(overhyped_anime_detector_query,conn)

print("\n Overhyped Animes:--")
print(overhyped_anime_detector)

#Close Connection

conn.close()

print("\nDatabase connection closed")

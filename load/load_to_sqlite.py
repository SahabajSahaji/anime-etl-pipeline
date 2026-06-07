import sqlite3
import pandas as pd
from pathlib import Path


csv_file=Path("data/processed/anime_clean.csv")

database_dir=Path("data/database")

database_dir.mkdir(parents=True ,exist_ok=True)

database_file=(database_dir/"anime.db")

#Read CSV file:---

print("Reading CSV ...")

df=pd.read_csv(csv_file)

print(f"Rows Loaded : {len(df)}")

#Create Database:---

conn=sqlite3.connect(database_file)

print("Connected to SQLite")

#Load to Database:---

df.to_sql(name="anime",con=conn,if_exists="replace",index=False)

print("Data Loaded into SQLite")

#Verify Data

query="""
SELECT COUNT(*) as Total_Anime 
FROM anime
"""

result=pd.read_sql(query,conn)

print(result)

conn.close()

print("Database Connection Closed...")
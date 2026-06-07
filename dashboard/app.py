import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Anime Analytic Dashboard",layout="wide")

st.title("Anime Analytics Dashboard")

#Database connection

database_file=Path("data/database/anime.db")
conn=sqlite3.connect(database_file)

query="""
SELECT *
FROM anime
"""

df=pd.read_sql(query,conn)

col1,col2,col3=st.columns(3)

col1.metric("Total Anime",len(df))

col2.metric("Average Score",round(df["score"].mean(),2))

col3.metric("Total Members",f"{df['members'].sum():,}")

st.subheader("Top Rated Anime")

top_rated = df.sort_values(
    by="score",
    ascending=False
).head(10)

st.dataframe(
    top_rated[
        ["title", "score", "members"]
    ]
)


st.subheader("Anime Released Per Year")

yearly = (df.groupby("year").size().reset_index(name="count"))

fig = px.line(yearly,x="year",y="count",markers=True)

st.plotly_chart(fig,use_container_width=True)


st.subheader("Hidden Gems")

hidden_gems = df.copy()

hidden_gems = hidden_gems[(hidden_gems["score"].notnull())
    &
    (hidden_gems["popularity"] > 0)]

hidden_gems["hidden_gem_score"] = (hidden_gems["score"]*hidden_gems["favorites"]/hidden_gems["popularity"])

hidden_gems = hidden_gems.sort_values(by="hidden_gem_score",ascending=False).head(20)

st.dataframe(hidden_gems[
       [
            "title",
            "score",
            "favorites",
            "popularity",
            "hidden_gem_score"
        ]
    ]

)


conn.close()
from extract.extract_api import extract_top_anime


def run_pipeline():
    df=extract_top_anime()
    print(df.head())

    df.to_csv("data/raw/top_anime.csv",index=False)


if __name__ =="__main__":
    run_pipeline()    
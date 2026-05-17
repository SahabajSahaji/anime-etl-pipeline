from extract.extract_api import extract_anime


def run_pipeline():
    df=extract_anime()
    print(df.head())

    df.to_csv("data/raw/anime.csv",index=False)


if __name__ =="__main__":
    run_pipeline()    
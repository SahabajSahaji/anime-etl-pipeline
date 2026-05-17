from extract.extract_api import extract_anime
from extract.extract_all_anime import extract_all_anime


def run_pipeline():
    # df=extract_anime()
    # print(df.head())

    # df.to_csv("data/raw/anime.csv",index=False)
    extract_all_anime()




if __name__ =="__main__":
    run_pipeline()    
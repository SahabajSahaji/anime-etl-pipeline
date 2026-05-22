from extract.extract_api import extract_anime
from extract.extract_all_anime import extract_all_anime


def run_pipeline():
    # df=extract_anime()
    # print(df.head())

    # df.to_csv("data/raw/anime.csv",index=False)
    extract_all_anime()
    #next work on Transformation
    #I Need some time to get to next step of the project
    # To be continued
    # I will work on you on Sunday




if __name__ =="__main__":
    run_pipeline()    
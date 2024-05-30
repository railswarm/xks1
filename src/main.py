from scatter import Scatter
#from steam import steam_scraper
from youtube import youtube_scraper


def main() -> None:
    scatter = Scatter()
    #steam_payloads = steam_scraper()
    #for x in steam_payloads:
    #    scatter.queue("STEAM", x.as_raw_list())
    for x in youtube_scraper():
        scatter.queue("Youtube", x.as_raw_list())
    scatter.send()

if __name__ == "__main__":
    main()

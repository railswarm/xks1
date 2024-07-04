from scatter import Scatter
from steam import steam_scraper
from youtube import youtube_scraper
import sys

def print_help() -> None:
    print("-s\tEnable scraping of Steam API\n-y\tEnable scraping of YouTube API\n-sy\tEnable scraping of both services")
    
def main() -> None:
    steam_f = False
    youtube_f = False
    
    if len(sys.argv) < 2:
        print("Invalid amount of keys. Use -h for help.")
        return

    match sys.argv[1]:
        case "-s":
            steam_f = True
        case "-y":
            youtube_f = True
        case "-sy":
            steam_f = True
            youtube_f = True
        case "-h":
            print_help()
            return
        case _:
            print("Invalid operator. Use -h key for help.")
            return
    
    #scatter = Scatter()
    if steam_f:
        print("Started scaping Steam API...")
        #for x in steam_scraper():
        #    scatter.queue("STEAM", x.as_raw_list())
    if youtube_f:
        print("Started scraping YouTube API...")
        #for x in youtube_scraper():
        #    scatter.queue("Youtube", x.as_raw_list())
        
    print("Sending payload to Google Sheets...")
    #scatter.send()
    print("Successfully sent data. Exiting.")

if __name__ == "__main__":
    main()

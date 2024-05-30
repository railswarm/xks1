import json
import requests

from dataclasses import dataclass
from utils import *

STEAM_GAMES_JSON_PATH = "steam_games.json"
DICTIONARY_PATH = "dictionary.txt"

@dataclass(frozen=True)
class SteamPayload:
    title: str
    ref: str
    genre: str
    review_score: int
    review_score_desc: str
    total_positive: int
    total_negative: int
    total_reviews: int
    recommendationid: int
    review: str
    voted_up: bool
    steamid: int
    num_games_owned: int
    num_reviews: int
    playtime_forever: int
    playtime_last_two_weeks: int
    playtime_at_review: int
    last_played: int
    timestamp_created: int
    timestamp_updated: int
    votes_up: int
    votes_funny: int
    weighted_vote_score: float
    comment_count: int
    
    def as_raw_list(self) -> list:
        return [
            '',
            self.title,
            '',
            self.ref,
            '',
            self.genre,
            str(self.review_score),
            str(self.review_score_desc),
            str(self.total_positive),
            str(self.total_negative),
            str(self.total_reviews),
            '',
            '',
            str(self.recommendationid),
            self.review,
            '',
            '',
            '',
            '',
            unix_timestamp_to_str(self.timestamp_created),
            bool_to_str(self.voted_up),
            str(self.steamid),
            str(self.num_games_owned),
            str(self.num_reviews),
            str(self.playtime_forever),
            str(self.playtime_last_two_weeks),
            str(self.playtime_at_review),
            unix_timestamp_to_str(self.last_played),
            unix_timestamp_to_str(self.timestamp_created),
            unix_timestamp_to_str(self.timestamp_updated),
            str(self.votes_up),
            str(self.votes_funny),
            str(self.weighted_vote_score),
            str(self.comment_count)
        ]

def get_steam_games(path: str) -> dict:    
    with open(path, 'r', encoding="utf-8-sig") as file:
        content = ''.join(file.readlines())
        return json.loads(content)

def steam_parser_get_new_url(cursor: str, game_id: str):
    main_ref = "https://store.steampowered.com/appreviews"
    args = f"filter=recent&language=russian&num_per_page=100&filter_offtopic_activity=0&cursor={cursor}&json=1"
    return f"{main_ref}/{game_id}?{args}"

def steam_parser_get_header(session, game_id: str):
    cursor = "*"
    url = steam_parser_get_new_url(cursor, game_id)
    response = session.get(url)
    data = json.loads(response.text)
    return data['query_summary']

def steam_parser_get_reviews(session, game_id: str) -> list:
    reviews = []
    cursors = set()
    
    cursor = "*"
    
    while cursor not in cursors:
        url = steam_parser_get_new_url(cursor, game_id)
        response = session.get(url)
        data = json.loads(response.text)
        
        cursors.add(cursor)
        
        try:
            cursor = data['cursor'].replace("+", "")
        except KeyError as error:
            print(f"Failed to retrieve cursor from response. URL: {url}, response <{response.status_code}>: {response.text}.")
            raise error
        except AttributeError as error:
            if data['success'] == 0:
                print(f"Expected valid cursor, found None, because data extraction wasn't successful.")
                raise error
            else:
                # Steam API doesn't provide valid cursor
                break
        
        reviews.extend(data['reviews'])
    
    return reviews

def steam_scraper() -> list:    
    session = requests.session()
    
    dictionary = load_dictionary(DICTIONARY_PATH)
    
    games = get_steam_games(STEAM_GAMES_JSON_PATH)

    payloads = []

    for game in games: 
        title = game
        ref = games[game]["ref"]
        genre = games[game]["genre"]
        
        header = steam_parser_get_header(session, game_id=games[game]["id"])
        reviews = steam_parser_get_reviews(session, game_id=games[game]["id"])
        
        probably_political_reviews = filter(
            lambda review: is_political(dictionary, review['review']) and in_date_range(review['timestamp_created']),
            reviews
        )
        
        for review in probably_political_reviews:
            payload = SteamPayload(
                title,
                ref,
                genre,
                header['review_score'],
                header['review_score_desc'],
                header['total_positive'],
                header['total_negative'],
                header['total_reviews'],
                review['recommendationid'],
                review['review'],
                review['voted_up'],
                review['author']['steamid'],
                review['author']['num_games_owned'],
                review['author']['num_reviews'],
                review['author']['playtime_forever'],
                review['author']['playtime_last_two_weeks'],
                review['author']['playtime_at_review'],
                review['author']['last_played'],
                review['timestamp_created'],
                review['timestamp_updated'],
                review['votes_up'],
                review['votes_funny'],
                review['weighted_vote_score'],
                review['comment_count']
            )
            
            payloads.append(payload)
    
    return payloads

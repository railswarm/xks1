import json


from dataclasses import dataclass
from googleapiclient.discovery import build
from datetime import datetime

from googleapiclient.errors import HttpError
from utils import *


# Maximum for `probably` political comments
MAX_POLITICAL_COMMENTS_PER_VIDEO = 1000

# Dictionary path for load_dictionary()
DICTIONARY_PATH = "dictionary.txt"

# JSON path of videos list
YOUTUBE_VIDEO_LIST_PATH = "youtube_videos.json"


@dataclass(frozen=True)
class YoutubeComment:
    channel_id: str
    text: str
    like_count: int
    published_at: datetime
    total_reply_count: int

@dataclass(frozen=True)
class YoutubePayload:
    video_title: str
    comment: YoutubeComment
    
    def as_raw_list(self) -> list:
        return [
            '', # Номер
            self.video_title,
            '', # Кто делал анализ?
            '', # Ссылка youtube
            ''  # Дата
            '', # Просмотры
            '', # Лайки
            '', # Комментарии
            '', # П+Л+К
            '', # % П от ПЛК
            '', # % Л от ПЛК
            '', # % К от ПЛК
            '', # Категория
            '', # Временной интервал
            '', # Тема
            '',
            str(self.comment.total_reply_count),
            self.comment.channel_id,
            self.comment.text,
            str(self.comment.like_count)
        ]

def youtube_parser_comment_from_raw(comment):
    channel_id = comment["topLevelComment"]["snippet"]["authorChannelId"]["value"]
    text = comment["topLevelComment"]["snippet"]["textOriginal"]
    like_count = comment["topLevelComment"]["snippet"]["likeCount"]
    published_at = datetime.fromisoformat(comment["topLevelComment"]["snippet"]["publishedAt"])
    total_reply_count = comment["totalReplyCount"]

    return YoutubeComment(
        channel_id,
        text,
        like_count,
        published_at,
        total_reply_count
    )

def youtube_parser_get_comments(service, dictionary, video_id: str) -> list:
    # API cursor
    page_token = None
    
    # Result
    comments = []

    while len(comments) < MAX_POLITICAL_COMMENTS_PER_VIDEO:
        try:    
            response = service.commentThreads().list(
                part="snippet",
                maxResults=100,
                textFormat="plainText",
                videoId=video_id,
                pageToken=page_token
            ).execute()
        except HttpError as err:
            print(f"Error occurred during data collection. video_id={video_id},reason={err}")
            break
            
        for item in response["items"]:
            comment = youtube_parser_comment_from_raw(item["snippet"])
                        
            if not comment.published_at.year == 2023:
                continue
            
            if is_political(dictionary, comment.text):
                comments.append(comment)
            
            try:
                replies = item["replies"]["comments"]
            except KeyError:
                # No replies found
                continue
            
            # Parse replies
            for reply in replies:
                comment = youtube_parser_comment_from_raw(reply["snippet"])
                    
                if is_political(dictionary, comment.text):
                    comments.append(comment)
            
            
        # Update cursor
        try:    
            page_token = response["nextPageToken"]
        except KeyError:
            # No more comments found
            break
    
    return comments[:MAX_POLITICAL_COMMENTS_PER_VIDEO]

def youtube_scraper():
    api_service_name = "youtube"
    api_version = "v3"
    developer_key = None

    with open("secret/youtube_api_token.txt", 'r') as file:
        developer_key = file.readline().rstrip()

    youtube = build(
        api_service_name,
        api_version,
        developerKey=developer_key
    )
    
    videos = None
    
    with open(YOUTUBE_VIDEO_LIST_PATH, 'r', encoding="utf-8-sig") as file:
        content = ''.join(file.readlines())
        videos = json.loads(content)
    
    dictionary = load_dictionary(DICTIONARY_PATH)
    
    payload = []

    for video in videos:
        comments = youtube_parser_get_comments(youtube, dictionary, videos[video]["id"])
        for comment in comments:
            payload.append(YoutubePayload(
                video_title=video,
                comment=comment
            ))
    
    return payload

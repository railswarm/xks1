import json

from googleapiclient.discovery import build

with open('refs.txt', 'r') as refs_raw:
    refs = [r.rstrip() for r in refs_raw.readlines()]
    
    ids = []

    for ref in refs:
        if 'shorts' in ref:
            video_id = ref.split("shorts/")[1][:11]
            ids.append(video_id)
        elif 'watch' in ref:
            video_id = ref.split("watch?v=")[1][:11]
            ids.append(video_id)
        elif 'youtu.be' in ref:
            video_id = ref.split("youtu.be/")[1][:11]
            ids.append(video_id)
        else:
            raise ValueError(f"Unknown ref pattern of ref={ref}")

    assert(all(map(lambda i: len(i) == 11, ids)))
    
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
    
    content = {}
    
    while len(ids) > 0:
        csv_ids = ','.join(ids[:50])
    
        r = youtube.videos().list(
            part="snippet",
            id=csv_ids
        ).execute()

        for i, vid in enumerate(r["items"]):
            video_title = vid["snippet"]["title"]
            video_id = ids[i]
            content[video_title] = {}
            content[video_title]["id"] = video_id
        
        ids = ids[50:]
    
    with open('youtube_videos.json', 'w', encoding="utf-8-sig") as file:
        json.dump(content, file, indent=4, ensure_ascii=False)

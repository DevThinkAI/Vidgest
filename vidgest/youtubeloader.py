from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YoutubeLoader:


    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)


    def get_videos(self, term, prev_days_to_search: int) -> list[dict[str, any]]:
        videos = []
        published_since_date = datetime.now() - timedelta(days=prev_days_to_search)
        request = self.youtube.search().list(
            part='snippet',
            q=term,
            order='viewCount',
            type='video',
            publishedAfter=f'{published_since_date.isoformat("T")}Z',
            maxResults=50
        )
        response = request.execute()
        videos = []
        for item in response['items']:
            video_id = item['id']['videoId']
            video_request = self.youtube.videos().list(
                part="statistics, contentDetails",
                id=video_id
            )
            video_response = video_request.execute()
            video = {
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'description': item['snippet']['description'],
                'channel_title': item['snippet']['channelTitle'],
                'video_id': video_id,
                'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                'view_count': int(video_response['items'][0]['statistics']['viewCount']),
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'duration': video_response['items'][0]['contentDetails']['duration'],
            }
            videos.append(video)
        return videos
    

    def get_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        except TranscriptsDisabled:
            # The video doesn't have a transcript
            return None

        text = " ".join([line["text"] for line in transcript])
        return text



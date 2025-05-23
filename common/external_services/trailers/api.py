# -*- coding: utf-8 -*-

import requests
from .response import YouTubeSearchResponse, Thumbnails, Id, Item, PageInfo, Snippet

from common import config_settings
from view import custom_console

class YtTrailer:
    url = 'https://www.googleapis.com/youtube/v3/search'

    def __init__(self, title: str):
        self.title = title
        self.params = {
            'part': 'snippet',
            'q': f'{title} trailer',
            'type': 'video',
            'key': config_settings.tracker_config.YOUTUBE_KEY,
            'channelId': '',
            'maxResults': 3,
        }

    def get_trailer_link(self) -> list[YouTubeSearchResponse] | None:

        # Use a favorite channel if the flag is True
        # Otherwise use a global YouTube search
        if config_settings.user_preferences.YOUTUBE_CHANNEL_ENABLE:
            self.params['channelId'] = config_settings.user_preferences.YOUTUBE_FAV_CHANNEL_ID

        response = requests.get(self.url, params=self.params)

        if response.status_code == 200:
            response_data = response.json()
            youtube_responses = []

            if response_data['items']:
                for result in response_data['items']:
                    thumbnails_data = result['snippet']['thumbnails']
                    thumbnails = Thumbnails(
                        default=thumbnails_data['default'],
                        high=thumbnails_data['high'],
                        medium=thumbnails_data['medium']
                    )

                    snippet_data = result['snippet']
                    snippet = Snippet(
                        channelId=snippet_data['channelId'],
                        channelTitle=snippet_data['channelTitle'],
                        description=snippet_data['description'],
                        liveBroadcastContent=snippet_data['liveBroadcastContent'],
                        publishTime=snippet_data['publishTime'],
                        publishedAt=snippet_data['publishedAt'],
                        title=snippet_data['title'],
                        thumbnails=thumbnails
                    )

                    video_id = None
                    # Sometimes it returns a chennelId and not only the video id
                    if 'id' in result:
                        id_data = result['id']

                        # Check if the result is a video or a channel
                        if id_data['kind'] == 'youtube#video':
                            video_id = Id(
                                kind=id_data.get('kind', ''),
                                videoId=id_data.get('videoId', '')
                            )
                        elif id_data['kind'] == 'youtube#channel':
                            # Get video_di from the result
                            video_id = Id(
                                kind=id_data.get('kind', ''),
                                videoId=id_data.get('channelId', '')
                            )
                        else:
                            # Fail
                            pass

                    item = Item(
                        etag=result['etag'],
                        id=video_id,
                        kind=result['kind'],
                        snippet=snippet
                    )

                    page_info = PageInfo(**response_data['pageInfo'])
                    youtube_response = YouTubeSearchResponse(
                        etag=response_data['etag'],
                        items=[item],
                        kind=response_data['kind'],
                        pageInfo=page_info,
                        regionCode=response_data['regionCode']
                    )
                    youtube_responses.append(youtube_response)


                return youtube_responses
            else:
                return None
        else:
            custom_console.wait_for_user_confirmation("No response from YouTube. Check your API_KEY\n"
                                              "Press Enter to continue or Ctrl-C to exit")
            return None
import json
import time
from functools import lru_cache
from typing import Generator, Literal

import requests
from bs4 import BeautifulSoup
from requests import HTTPError
from requests_html import HTMLSession

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, YOUTUBE_BASE_URL, DEFAULT_VIDEO_LIMIT, DEFAULT_USER_AGENT


class YouTube(Collector):
    """
    This class allows you to collect metadata about a YouTube account.
    """

    __type_property_map = {
        "videos": "videoRenderer",
        "streams": "videoRenderer",
        "shorts": "reelItemRenderer"
    }

    def __init__(self, video_limit: int = DEFAULT_VIDEO_LIMIT, timeout: int = DEFAULT_TIMEOUT, proxy=None):
        super().__init__(timeout, proxy)
        self.proxy = proxy
        self.timeout = timeout
        self.video_limit = video_limit
        self.session = HTMLSession()
        self.session.headers["User-Agent"] = DEFAULT_USER_AGENT
        self.session.headers["Accept-Language"] = "en"

    @lru_cache
    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's Github account
        :param username:
        :return: A dict of a user's GitHub account.
        """

        headers = {}
        response = self.session.get(f"{YOUTUBE_BASE_URL}{username}", headers=headers)

        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Execute the javascript
        response.html.render(sleep=1)
        user_data = {}

        # Now parse the incoming data
        soup = BeautifulSoup(response.html.html, "html.parser")
        user_data['username'] = soup.find(id='channel-handle').text

        user_data['channel_name'] = soup.find(class_="style-scope ytd-channel-name").text.strip()

        subscriber_count = YouTube.__parse_subscriber_count(soup.find(id='subscriber-count').text)
        user_data['subscriber_count'] = subscriber_count

        video_count = YouTube.__parse_subscriber_count(soup.find(id='videos-count').text)
        user_data['video_count'] = video_count

        user_data['description'] = soup.find("meta", itemprop="description")['content']

        channel_data = self.get_channel(username, limit=10)
        videos = []
        for video in channel_data:
            videos.append(video)

        user_data['videos'] = videos
        return user_data

    @lru_cache
    def get_channel(self, channel_username: str = None,
                    limit: int = None,
                    sleep: float = 1,
                    sort_by: Literal["newest", "oldest", "popular"] = "newest",
                    content_type: Literal["videos", "shorts", "streams"] = "videos",
                    ) -> Generator[dict, None, None]:
        """Get videos for a channel.

        Parameters:
            channel_username (``str``, *optional*):
                The username from the channel you want to get the videos for.
                Ex. ``LinusTechTips`` (without the @).
                If you prefer to use the channel url instead, see ``channel_url`` above.

            limit (``int``, *optional*):
                Limit the number of videos you want to get.

            sleep (``int``, *optional*):
                Seconds to sleep between API calls to YouTube, in order to prevent getting blocked.
                Defaults to 1.

            sort_by (``str``, *optional*):
                In what order to retrieve to videos. Pass one of the following values.
                ``"newest"``: Get the new videos first.
                ``"oldest"``: Get the old videos first.
                ``"popular"``: Get the popular videos first. Defaults to "newest".

            content_type (``str``, *optional*):
                In order to get content type. Pass one of the following values.
                ``"videos"``: Videos
                ``"shorts"``: Shorts
                ``"streams"``: Streams
        """

        base_url = f"https://www.youtube.com/@{channel_username}"

        url = f"{base_url}/{content_type}?view=0&flow=grid"

        api_endpoint = "https://www.youtube.com/youtubei/v1/browse"
        videos = self.get_videos(url, api_endpoint, YouTube.__type_property_map[content_type], limit, sleep, sort_by)
        for video in videos:
            yield video

    @lru_cache
    def get_videos(self, url: str, api_endpoint: str, selector: str, limit: int, sleep: float, sort_by: str = None
                   ) -> Generator[dict, None, None]:
        session = YouTube.__get_session()
        is_first = True
        quit_it = False
        count = 0
        while True:
            if is_first:
                html = self.__get_initial_data(self.session, url)
                client = json.loads(
                    YouTube.__get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
                )["client"]
                api_key = YouTube.__get_json_from_html(html, "innertubeApiKey", 3)
                self.session.headers["X-YouTube-Client-Name"] = "1"
                self.session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
                data = json.loads(
                    YouTube.__get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
                )
                next_data = YouTube.__get_next_data(data, sort_by)
                is_first = False
                if sort_by and sort_by != "newest":
                    continue
            else:
                data = self.__get_ajax_data(self.session, api_endpoint, api_key, next_data, client)
                next_data = YouTube.__get_next_data(data)
            for result in self.__get_videos_items(data, selector):
                try:
                    count += 1
                    yield result
                    if count == limit:
                        quit_it = True
                        break
                except GeneratorExit:
                    quit_it = True
                    break

            if not next_data or quit_it:
                break

            time.sleep(sleep)

        session.close()

    @staticmethod
    def __get_session() -> requests.Session:
        session = requests.Session()
        session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        session.headers["Accept-Language"] = "en"
        return session

    @staticmethod
    def __get_initial_data(session: requests.Session, url: str) -> str:
        session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
        response = session.get(url, params={"ucbcb": 1})

        html = response.text
        return html

    @staticmethod
    def __get_ajax_data(session: requests.Session, api_endpoint: str,
                        api_key: str,
                        next_data: dict,
                        client: dict,
                        ) -> dict:
        data = {
            "context": {"clickTracking": next_data["click_params"], "client": client},
            "continuation": next_data["token"],
        }
        response = session.post(api_endpoint, params={"key": api_key}, json=data)
        return response.json()

    @staticmethod
    def __get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
        pos_begin = html.find(key) + len(key) + num_chars
        pos_end = html.find(stop, pos_begin)
        return html[pos_begin:pos_end]

    @staticmethod
    def __get_next_data(data: dict, sort_by: str = None) -> dict:
        sort_by_map = {
            "newest": 0,
            "popular": 1,
            "oldest": 2,
        }
        if sort_by and sort_by != "newest":
            endpoint = next(
                YouTube.__search_dict(data, "feedFilterChipBarRenderer"), None)["contents"][sort_by_map[sort_by]][
                "chipCloudChipRenderer"]["navigationEndpoint"]
        else:
            endpoint = next(YouTube.__search_dict(data, "continuationEndpoint"), None)
        if not endpoint:
            return None
        next_data = {
            "token": endpoint["continuationCommand"]["token"],
            "click_params": {"clickTrackingParams": endpoint["clickTrackingParams"]},
        }

        return next_data

    @staticmethod
    def __search_dict(partial: dict, search_key: str) -> Generator[dict, None, None]:
        stack = [partial]
        while stack:
            current_item = stack.pop(0)
            if isinstance(current_item, dict):
                for key, value in current_item.items():
                    if key == search_key:
                        yield value
                    else:
                        stack.append(value)
            elif isinstance(current_item, list):
                for value in current_item:
                    stack.append(value)

    @staticmethod
    def __get_videos_items(data: dict, selector: str) -> Generator[dict, None, None]:
        return YouTube.__search_dict(data, selector)

    @staticmethod
    def __parse_subscriber_count(count_value: str) -> int:
        """
        Google truncates the number of videos, views and subscribers.  This reverses the process
        and gets you ints instead of text.
        Args:
            count_value: The input value

        Returns: An integer representation of the input value.

        """
        parts = count_value.split()
        subscriber_count = YouTube.__value_to_int(parts[0])
        return int(subscriber_count)

    @staticmethod
    @lru_cache
    def __value_to_int(num: str) -> int:
        """
        This function converts numbers formatted for display into ints.
        """
        result = 0
        if isinstance(num, (float, int)):
            result = int(num)
        elif 'K' in num:
            if len(num) > 1:
                result = int(float(num.replace('K', '')) * 1000)
            else:
                result = 1000
        elif 'M' in num:
            if len(num) > 1:
                result = int(float(num.replace('M', '')) * 1000000)
            else:
                result = 1000000
        elif 'B' in num:
            if len(num) > 1:
                result = int(float(num.replace('B', '')) * 1000000000)
            else:
                result = 1000000000
        return result

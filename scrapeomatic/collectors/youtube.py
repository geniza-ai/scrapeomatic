from functools import lru_cache

import scrapetube
import ua_generator
from bs4 import BeautifulSoup
from requests import HTTPError
from requests_html_playwright.requests_html import HTMLSession

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_VIDEO_LIMIT, DEFAULT_TIMEOUT, YOUTUBE_BASE_URL


class YouTube(Collector):
    """
    This class allows you to collect metadata about a YouTube account.
    """

    def __init__(self, video_limit: int = DEFAULT_VIDEO_LIMIT,
                 timeout: int = DEFAULT_TIMEOUT,
                 proxy=None, cert_path: str = None):
        super().__init__(timeout, proxy, cert_path=cert_path)
        self.proxy = proxy
        self.timeout = timeout
        self.video_limit = video_limit
        self.user_agent = ua_generator.generate()
        self.session = HTMLSession()
        self.session.headers["User-Agent"] = self.user_agent.text
        self.session.headers["Accept-Language"] = "en"

    @lru_cache()
    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's Github account
        :param username:
        :return: A dict of a user's YouTube account.
        """
        user_data = {}

        session = HTMLSession()
        session.headers["User-Agent"] = self.user_agent.text
        session.headers["Accept-Language"] = "en"

        headers = {}
        response = session.get(f"{YOUTUBE_BASE_URL}{username}", headers=headers)

        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Execute the javascript
        response.html.render()

        # Now parse the incoming data
        soup = BeautifulSoup(response.html.html, "html.parser")

        user_data['username'] = username

        if soup.find(class_="style-scope ytd-channel-name"):
            user_data['channel_name'] = soup.find(class_="style-scope ytd-channel-name").text.strip()

        if soup.find(id='subscriber-count'):
            subscriber_count = YouTube.__parse_subscriber_count(soup.find(id='subscriber-count').text)
            user_data['subscriber_count'] = subscriber_count

        if soup.find(id='videos-count'):
            video_count = YouTube.__parse_subscriber_count(soup.find(id='videos-count').text)
            user_data['video_count'] = video_count

        if soup.find("meta", itemprop="description"):
            user_data['description'] = soup.find("meta", itemprop="description")['content']

        videos = self.get_channel(username)

        video_list = []
        for video in videos:
            video_list.append(video)

        user_data['videos'] = video_list

        # Don't forget to tidy up.
        session.close()
        return user_data

    @lru_cache()
    def get_channel(self, channel_username: str) -> dict:
        return scrapetube.get_channel(channel_username=channel_username,
                                      limit=self.video_limit
                                      )

    @lru_cache()
    def get_video(self, video_id: str) -> dict:
        """
        Gets the metadata for a particular video.
        Args:
            video_id: The google id for the video.

        Returns:

        """
        return scrapetube.scrapetube.get_video(video_id)


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

import json
import logging
from functools import lru_cache
from urllib.parse import quote

import ua_generator
from requests import HTTPError, JSONDecodeError

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import INSTAGRAM_BASE_URL, INSTAGRAM_PROFILE_URL, DEFAULT_TIMEOUT, \
    INSTAGRAM_APP_ID, INSTAGRAM_VIDEO_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')


class Instagram(Collector):

    def __init__(self, timeout=DEFAULT_TIMEOUT, proxy=None, cert_path=None):
        super().__init__(timeout, proxy, cert_path)
        self.proxy = proxy
        self.cert_path = cert_path
        self.timeout = timeout

    @lru_cache
    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's Instagram account.  Note that the account must be public.
        :param username: The Instagram username you want to explore.
        :return:  A dictionary of metadata about the Instagram profile.
        """
        headers = Instagram.__build_headers(username)
        params = Instagram.__build_param(username)
        response = self.make_request(url=INSTAGRAM_PROFILE_URL, headers=headers, params=params)
        if response.status_code != 200:
            logging.error(f"Error retrieving Instagram profile for {username}.  Status Code: {response.status_code}")
            raise HTTPError(f"Error retrieving Instagram profile for {username}.  Status Code: {response.status_code}")

        if len(response.text) == 0:
            raise HTTPError("Empty response from Instagram. Your IP may be blocked or the profile you are trying to access maybe private.")
        try:
            return response.json()['data']['user']
        except JSONDecodeError as exc:
            error_message = f"Error parsing Instagram profile. Your IP could be blocked or the profile could be private. Response was: {response.text}. {exc}"
            logging.error(error_message)
            raise HTTPError(error_message) from exc

    @lru_cache
    def get_post(self, url_or_shortcode: str) -> dict:
        """
        Scrapes a post from Instagram.  You can provide either the complete URL or the short code from the URL.
        Sourced from https://scrapfly.io/blog/how-to-scrape-instagram/
        Args:
            url_or_shortcode: URL or the short code.

        Returns:  A dictionary of data about the post.

        """

        if "http" in url_or_shortcode:
            shortcode = url_or_shortcode.split("/p/")[-1].split("/")[0]
        else:
            shortcode = url_or_shortcode
        logging.debug(f"scraping instagram post: {shortcode}")

        variables = {
            "shortcode": shortcode,
            "child_comment_count": 20,
            "fetch_comment_count": 100,
            "parent_comment_count": 24,
            "has_threaded_comments": True
        }

        url = INSTAGRAM_VIDEO_URL + quote(json.dumps(variables))

        headers = {"x-ig-app-id": INSTAGRAM_APP_ID}
        response = self.make_request(url=url, headers=headers)
        data = json.loads(response.text)
        return data["data"]["shortcode_media"]

    @staticmethod
    def __build_param(username: str) -> dict:
        return {
            'username': username,
        }

    @staticmethod
    @lru_cache
    def __build_headers(username: str) -> dict:
        user_agent = ua_generator.generate()
        return {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f"{INSTAGRAM_BASE_URL}/{username}/",
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': user_agent.ch.brands,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent.text,
            'x-asbd-id': '198387',
            'x-csrftoken': 'VUm8uVUz0h2Y2CO1SwGgVAG3jQixNBmg',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'x-requested-with': 'XMLHttpRequest',
        }

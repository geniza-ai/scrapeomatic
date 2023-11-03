import requests
from fake_headers import Headers
from requests import HTTPError

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import INSTAGRAM_BASE_URL, INSTAGRAM_PROFILE_URL


class Instagram(Collector):

    def __init__(self, timeout=5, proxy=None):
        self.proxy = proxy
        self.timeout = timeout

    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's Instagram
        :param username:
        :return:
        """
        headers = Instagram.__build_headers(username)
        params = Instagram.__build_param(username)
        response = self.__make_request(url=INSTAGRAM_PROFILE_URL, headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")
        return response.json()['data']['user']

    @staticmethod
    def __build_param(username):
        return {
            'username': username,
        }

    @staticmethod
    def __build_headers(username):
        return {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f"{INSTAGRAM_BASE_URL}/{username}/",
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Microsoft Edge";v="108"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': Headers().generate()['User-Agent'],
            'x-asbd-id': '198387',
            'x-csrftoken': 'VUm8uVUz0h2Y2CO1SwGgVAG3jQixNBmg',
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': '0',
            'x-requested-with': 'XMLHttpRequest',
        }

    def __make_request(self, url, params, headers):
        if self.proxy:
            proxy_dict = {
                'http': f'http://{self.proxy}',
                'https': f'http://{self.proxy}'
            }
            return requests.get(url, headers=headers, timeout=self.timeout, params=params, proxies=proxy_dict)

        return requests.get(url, timeout=self.timeout, headers=headers, params=params)

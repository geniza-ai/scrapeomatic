import json
import logging
from json import JSONDecodeError
from pprint import pprint

import emoji
from bs4 import BeautifulSoup
from requests import HTTPError
import ua_generator

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, TIKTOK_BASE_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')
HEADERS = {'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': ua_generator.generate().text,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive'}


class TikTok2(Collector):

    def __init__(self, proxy=None, cert_path=None):
        super().__init__(DEFAULT_TIMEOUT, proxy, cert_path)

    def collect(self, username: str) -> dict:
        """
        This function will and return all publicly available information from the users' TikTok profile.
        :param username: The username whose info you wish to gather.
        :return: A dict of the user's account information.
        """

        if username.startswith('@'):
            final_url = f"{TIKTOK_BASE_URL}{username}"
        else:
            final_url = f"{TIKTOK_BASE_URL}{username}"

        headers = {}
        response = self.make_request(url=final_url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Now parse the incoming data
        soup = BeautifulSoup(response.text, "html5lib")

        # The user info is contained in a large JS object
        tt_script = soup.find('script', attrs={'id': "__UNIVERSAL_DATA_FOR_REHYDRATION__"})
        try:
            raw_json = json.loads(tt_script.string)
        except AttributeError as exc:
            raise JSONDecodeError(f"ScrapeOMatic was unable to parse the data from TikTok.  Please try again.") from exc

        user_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']
        stats_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['stats']
        profile_data = {
            'sec_id': user_data['secUid'],
            'id': user_data['id'],
            'is_secret': user_data['secret'],
            'username': user_data['uniqueId'],
            'bio': emoji.demojize(user_data['signature'], delimiters=("", "")),
            'avatar_image': user_data['avatarMedium'],
            'following': stats_data['followingCount'],
            'followers': stats_data['followerCount'],
            'language': user_data['language'],
            'nickname': emoji.demojize(user_data['nickname'], delimiters=("", "")),
            'hearts': stats_data['heart'],
            'region': user_data['region'],
            'verified': user_data['verified'],
            'heart_count': stats_data['heartCount'],
            'video_count': stats_data['videoCount'],
            'is_verified': user_data['verified'],
            # 'videos': videos,
            # 'hashtags': self.hashtags
        }

        pprint(profile_data)
        return {}


if __name__ == '__main__':
    tiktok2 = TikTok2()
    results = tiktok2.collect('tara_town')

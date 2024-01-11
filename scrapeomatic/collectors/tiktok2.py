import json
import logging
from time import time
from json import JSONDecodeError
from pprint import pprint
from urllib.parse import urlencode

import emoji
from bs4 import BeautifulSoup
from requests import HTTPError
import ua_generator

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, TIKTOK_BASE_URL
from scrapeomatic.utils.tiktok.xbogus import Signer

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
        super().__init__(DEFAULT_TIMEOUT, proxy, cert_path, True)

    def collect(self, username: str) -> dict:
        """
        This function will and return all publicly available information from the users' TikTok profile.
        :param username: The username whose info you wish to gather.
        :return: A dict of the user's account information.
        """

        final_url = f"{TIKTOK_BASE_URL}/@{username}"

        response = self.make_request(url=final_url, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Now parse the incoming data
        soup = BeautifulSoup(response.text, "html5lib")

        f = open("tiktok.html", "w")
        f.write(response.text)
        f.close()

        # The user info is contained in a large JS object
        tt_script = soup.find('script', attrs={'id': "__UNIVERSAL_DATA_FOR_REHYDRATION__"})
        try:
            raw_json = json.loads(tt_script.string)
        except AttributeError as exc:
            raise JSONDecodeError(f"ScrapeOMatic was unable to parse the data from TikTok.  Please try again.") from exc

        user_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']
        stats_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['stats']

        videos = self.get_videos(username, user_data['secUid'])

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
        return profile_data

    def get_videos(self, username: str, secUid: str) -> list:
        user_agent = ua_generator.generate()
        video_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'www.tiktok.com',
            'Referer': f"{TIKTOK_BASE_URL}/@{username}",
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'User-Agent': user_agent.text
        }

        query_params = {
            'aid': 1988,
            'app_language': 'en',
            'app_name': 'tiktok_web',
            'browser_language': 'en-US',
            'browser_name': 'Mozilla',
            'browser_online': True,
            'browser_platform': user_agent.platform,
            'browser_version': user_agent.browser_version,
            'channel': 'tiktok_web',
            'cookie_enabled': True,
            'count': 35,
            'coverFormat': 0,
            'cursor': 0,
            'device_id': '7280579273231795755',  # TODO Fix ME
            'device_platform': 'web_pc',
            'focus_state': True,
            'from_page': 'user',
            'priority_region': '',
            'referer': '',
            'region': 'US',
            'screen_height': 1440,
            'screen_width': 2550,
            'secUid': secUid,
            'tz_name': 'America/New_York',
            'webcast_language': 'en',
            #'ms_token': '',  # ??
            '_signature': '',
            'WebIdLastTime': int(time())
        }

        query = urlencode(query_params)



        xbogus = Signer.sign(query, user_agent.text)

        final_url = f"{TIKTOK_BASE_URL}/api/post/item_list?{xbogus}"

        print(f"Making call to get videos: {final_url}")
        response = self.make_request(url=final_url, headers=video_headers)
        print(response.status_code)
        print(response.text)


if __name__ == '__main__':
    tiktok2 = TikTok2()
    results = tiktok2.collect('tara_town')

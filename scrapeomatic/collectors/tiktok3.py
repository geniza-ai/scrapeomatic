import json
import logging
from json import JSONDecodeError
from pprint import pprint
import random
from time import time
from urllib.parse import urlencode

import chromedriver_autoinstaller
import emoji
import ua_generator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup

from scrapeomatic.collector import Collector
from scrapeomatic.utils.tiktok.xbogus import Signer
from scrapeomatic.utils.utils import Utils
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, TIKTOK_BASE_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', level=logging.DEBUG)

ua = ua_generator.generate()
user_agent = ua.text

HEADERS = {'Accept-Encoding': 'gzip, deflate, sdch',
           'Accept-Language': 'en-US,en;q=0.8',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': user_agent,
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive'}


class TikTok3(Collector):

    def __init__(self, proxy=None, cert_path=None):
        super().__init__(DEFAULT_TIMEOUT, proxy, cert_path)
        chromedriver_autoinstaller.install()
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-extensions')
        options.add_argument('--incognito')
        options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')
        options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')

        self.driver = webdriver.Chrome(options=options)

    def collect(self, username: str) -> dict:
        """
        This function will and return all publicly available information from the users' TikTok profile.
        :param username: The username whose info you wish to gather.
        :return: A dict of the user's account information.
        """

        final_url = f"{TIKTOK_BASE_URL}/@{username}"
        # self.driver.implicitly_wait(5)
        self.driver.get(final_url)

        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        f = open("tiktok3.html", "w")
        f.write(html)
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

        # pprint(profile_data)
        return profile_data

    def get_videos(self, username: str, secUid: str) -> list:
        video_list = []
        cookies_dict = Utils.get_cookie_dict(self.driver)
        device_id = str(random.randint(10 ** 18, 10 ** 19 - 1))
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
            'User-Agent': user_agent
        }

        query_params = {
            'WebIdLastTime': 1701317720,
            'aid': 1988,
            'app_language': 'en',
            'app_name': 'tiktok_web',
            'browser_language': 'en-US',
            'browser_name': 'Mozilla',
            'browser_online': "true",
            'browser_platform': ua.platform,
            'browser_version': ua.browser_version,
            'channel': 'tiktok_web',
            'cookie_enabled': "true",
            'count': 35,
            'coverFormat': 0,
            'cursor': 0,
            'device_id': 7307103952481502762,
            'device_platform': 'web_pc',
            'focus_state': "true",
            'from_page': 'user',
            'history_length': 9,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            'priority_region': '',
            'referer': '',
            'region': 'US',
            'screen_height': 1440,
            'screen_width': 2550,
            'secUid': secUid,
            'tz_name': 'America/New_York',
            'webcast_language': 'en',
            'ms_token': cookies_dict['msToken'],
            '_signature': '',
        }
        query = urlencode(query_params)
        logging.debug("User agent: %s", user_agent)
        xbogus = Signer.sign(query, user_agent)

        final_url = f"{TIKTOK_BASE_URL}/api/post/item_list?{xbogus}"

        self.driver.get(final_url)
        print(self.driver.page_source)

        return video_list


    def __set_session_params(self, session):
        """Set the session params for a TikTokPlaywrightSession"""
        user_agent = session.page.evaluate("() => navigator.userAgent")
        language = "en"
        platform = session.page.evaluate("() => navigator.platform")
        device_id = str(random.randint(10**18, 10**19 - 1))  # Random device id
        history_len = str(random.randint(1, 10))  # Random history length
        screen_height = str(random.randint(600, 1080))  # Random screen height
        screen_width = str(random.randint(800, 1920))  # Random screen width
        timezone = session.page.evaluate(
            "() => Intl.DateTimeFormat().resolvedOptions().timeZone"
        )

        session_params = {
            "aid": "1988",
            "app_language": language,
            "app_name": "tiktok_web",
            "browser_language": language,
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": platform,
            "browser_version": user_agent,
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": device_id,
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": history_len,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": language,
            "os": platform,
            "priority_region": "",
            "referer": "",
            "region": "US",  # TODO: TikTokAPI option
            "screen_height": screen_height,
            "screen_width": screen_width,
            "tz_name": timezone,
            "webcast_language": language,

        }
        session.params = session_params


if __name__ == '__main__':
    tiktok3 = TikTok3()
    results = tiktok3.collect('tara_town')

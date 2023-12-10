import logging

import emoji
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions
from fake_headers import Headers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_BROWSER, TIKTOK_BASE_URL, DEFAULT_TIMEOUT

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')


class TikTok(Collector):

    def __init__(self, browser_name=None, proxy=None):
        super().__init__(DEFAULT_TIMEOUT, proxy)
        # Initialize the driver.  Default to chrome
        self.hashtags = {}
        self.proxy = proxy
        if not browser_name:
            browser_name = DEFAULT_BROWSER

        browser_name = browser_name.strip().lower()

        if browser_name == "chrome":
            browser_option = ChromeOptions()
            browser_option = self.__set_properties(browser_option)

            # Add proxy server if present.
            if self.proxy is not None:
                browser_option.add_argument(f'--proxy-server={self.proxy}')

            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=browser_option)
        elif browser_name == "firefox":
            browser_option = FirefoxOptions()
            browser_option = self.__set_properties(browser_option)
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=browser_option)
        else:
            raise ValueError("Invalid browser choice. Options are chrome or firefox.")

    def collect(self, username: str) -> dict:
        """
        This function will and return all publicly available information from the users' TikTok profile.
        :param username: The username whose info you wish to gather.
        :return: A dict of the user's account information.
        """

        final_url = f"{TIKTOK_BASE_URL}{username}"

        try:
            self.driver.get(final_url)
        except AttributeError as exc:
            raise AttributeError(f"Error retrieving data from URL: {final_url}") from exc

        wait = WebDriverWait(self.driver, 5)
        wait.until(expected_conditions.title_contains(f"@{username}"))

        state_data = self.driver.execute_script("return window['SIGI_STATE']")
        user_data = state_data['UserModule']['users'][username.lower()]
        stats_data = state_data['UserModule']['stats'][username.lower()]
        videos = self.__get_videos(state_data['ItemModule'])
        self.hashtags = self.__sort_dict(self.hashtags)

        profile_data = {
            'sec_id': user_data['secUid'],
            'id': user_data['id'],
            'is_secret': user_data['secret'],
            'username': user_data['uniqueId'],
            'bio': emoji.demojize(user_data['signature'], delimiters=("", "")),
            'avatar_image': user_data['avatarMedium'],
            'following': stats_data['followingCount'],
            'followers': stats_data['followerCount'],
            'hearts': stats_data['heart'],
            'heart_count': stats_data['heartCount'],
            'video_count': stats_data['videoCount'],
            'is_verified': user_data['verified'],
            'videos': videos,
            'hashtags': self.hashtags
        }
        return profile_data

    def close(self):
        self.driver.close()
        self.driver.quit()

    @staticmethod
    def __set_properties(browser_option):
        user_agent = Headers().generate()
        browser_option.add_argument('--headless')
        browser_option.add_argument('--disable-extensions')
        browser_option.add_argument('--incognito')
        browser_option.add_argument("--no-sandbox")
        browser_option.add_argument("--disable-dev-shm-usage")
        browser_option.add_argument('--disable-gpu')
        browser_option.add_argument('--log-level=3')
        browser_option.add_argument(f'user-agent={user_agent}')
        browser_option.add_argument('--disable-notifications')
        browser_option.add_argument('--disable-popup-blocking')

        return browser_option

    @staticmethod
    def __sort_dict(hashtag_dict: dict) -> dict:
        sorted_hashtags = sorted(hashtag_dict.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_hashtags)

    def __get_videos(self, item_list: dict) -> list:
        video_list = []
        for item in item_list.values():
            video = {}
            hashtags = []
            # Get the video description
            video['description'] = emoji.demojize(item['desc'], delimiters=("", ""))
            video['nickname'] = emoji.demojize(item['nickname'], delimiters=("", ""))
            video['stats'] = item['stats']
            video['create_date'] = item['createTime']
            video['location_created'] = item['locationCreated']

            long_desc = ""
            # Get Longer Description
            for challenge in item['challenges']:
                if len(long_desc) > 0 and len(challenge['desc']) > 0:
                    long_desc += "\n"
                long_desc += challenge['desc']
            video['long_desc'] = long_desc

            # Get the hashtags
            for tag in item['textExtra']:
                # skip empty hashtags
                if len(tag) == 0:
                    continue

                # Convert to lower case and remove leading and trailing whitespace.
                hashtag = tag['hashtagName'].lower().strip()

                # Check length again...
                if not hashtag or len(hashtag) == 0:
                    continue

                hashtags.append(hashtag)

                hashtag_keys = self.hashtags.keys()
                # Add to global list
                if hashtag not in hashtag_keys:
                    self.hashtags[hashtag] = 1
                else:
                    self.hashtags[hashtag] += 1

            video['hashtags'] = hashtags
            video_list.append(video)

        return video_list

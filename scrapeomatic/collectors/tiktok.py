import json
import logging
from pprint import pprint

import emoji
import ua_generator
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from requests import JSONDecodeError

from scrapeomatic.collector import Collector
from scrapeomatic.utils.async_utils import AsyncUtils
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, TIKTOK_BASE_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', level=logging.INFO)

ua = ua_generator.generate()
user_agent = ua.text


class TikTok(Collector):

    def __init__(self, proxy: str = None, cert_path: str = None, timeout: int = DEFAULT_TIMEOUT):
        super().__init__(DEFAULT_TIMEOUT, proxy, cert_path)
        self.timeout = timeout * 1000

    def collect(self, username: str) -> dict:
        _xhr_calls = []
        final_url = f"{TIKTOK_BASE_URL}{username}"

        def intercept_response(response):
            """Capture all background requests and save them."""
            # We can extract details from background requests
            if response.request.resource_type == "xhr":
                logging.debug(f"Appending {response.request.url}")
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw_firefox:
            browser = pw_firefox.firefox.launch(headless=True, timeout=self.timeout)
            context = browser.new_context(viewport={"width": 1920, "height": 1080},
                                          strict_selectors=False)
            page = context.new_page()

            # Block cruft
            page.route("**/*", AsyncUtils.intercept_route)

            # Enable background request intercepting:
            page.on("response", intercept_response)

            # Navigate to the profile page
            response = page.goto(final_url, referer=final_url)
            page.wait_for_timeout(1500)

            if response.status != 200:
                logging.error(f"Bad response: {response}")
                raise ValueError(f"Error retrieving page: {response}")

            # Get the page content
            html = page.content()

            # Parse it.
            soup = BeautifulSoup(html, 'html.parser')

            # The user info is contained in a large JS object called __UNIVERSAL_DATA_FOR_REHYDRATION__.
            tt_script = soup.find('script', attrs={'id': "__UNIVERSAL_DATA_FOR_REHYDRATION__"})

            try:
                raw_json = json.loads(tt_script.string)
            except AttributeError as exc:
                raise JSONDecodeError(
                    f"ScrapeOMatic was unable to parse the data from TikTok user {username}. Please try again.\n {exc}") from exc

            if "userInfo" not in raw_json['__DEFAULT_SCOPE__']['webapp.user-detail'].keys():
                raise ValueError(f"No profile found for user {username}")

            user_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']
            stats_data = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['stats']

            # button = page.get_by_text('p:has-text("Continue as guest")')
            # guest_button = page.locator(selector="div", has=button)
            # if guest_button is not None:
            #     logging.debug("Clicking button.")
            #     guest_button.click(no_wait_after=True)

            # page.click('.css-dcgpa6-DivBoxContainer');
            # page.click('.emuynwa3');
            # page.wait_for_timeout(500)
            # page.keyboard.press("PageDown")
            # page.wait_for_timeout(500)
            # page.keyboard.press("PageDown")

            data_calls = [f for f in _xhr_calls if "list" in f.url]
            for call in data_calls:
                logging.debug(call.json())

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

            return profile_data


if __name__ == '__main__':
    tiktok = TikTok()
    results = tiktok.collect('brookemonk_')
    pprint(results)

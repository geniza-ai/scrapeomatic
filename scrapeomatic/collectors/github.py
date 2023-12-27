from functools import lru_cache

from bs4 import BeautifulSoup
from requests import HTTPError

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import GITHUB_BASE_URL, DEFAULT_TIMEOUT


class GitHub(Collector):

    def __init__(self, timeout=DEFAULT_TIMEOUT, proxy=None, cert_path=None):
        super().__init__(timeout, proxy, cert_path)
        self.proxy = proxy
        self.cert_path = cert_path
        self.timeout = timeout

    @lru_cache
    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's Github account
        :param username:
        :return: A dict of a user's GitHub account.
        """
        headers = {}
        response = self.make_request(url=f"{GITHUB_BASE_URL}/{username}", headers=headers)
        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Now parse the incoming data
        soup = BeautifulSoup(response.text, "html5lib")
        user_data = {}

        user_data['full_name'] = soup.find(itemprop="name").get_text().strip()
        user_data['additional_name'] = soup.find(itemprop="additionalName").get_text().strip()
        user_data['bio'] = soup.find("div", class_="p-note user-profile-bio mb-3 js-user-profile-bio f4").get(
            'data-bio-text').strip()
        # FIX THIS: Email not being picked up
        user_data['email'] = soup.find(itemprop="email")
        user_data['works_for'] = soup.find(itemprop="worksFor").get_text().strip()
        user_data['location'] = soup.find(itemprop="homeLocation").get_text().strip()
        user_data['url'] = soup.find(itemprop="url").get_text().strip()

        # GitHub allows multiple social media accounts
        user_data['social'] = {}
        social_data = soup.findAll(itemprop="social")
        for account in social_data:
            account_parts = GitHub.__get_social_media_accounts(account.get_text())
            user_data['social'][account_parts['platform']] = account_parts['username']

        # Get pinned items
        raw_pinned_items = soup.find_all(class_="pinned-item-list-item-content")
        user_data['pinned_items'] = GitHub.__get_pinned_items(raw_pinned_items)

        return user_data

    @staticmethod
    @lru_cache
    def __get_social_media_accounts(raw_info: str) -> dict:
        """
        This method extracts the various social media accounts a user may have on their github account.
        """
        parts = raw_info.rstrip().lstrip().split()

        # Remove empty elements
        parts = list(filter(None, parts))
        result = {'platform': parts[0].strip(), 'username': parts[1].strip()}
        return result

    @staticmethod
    def __get_pinned_items(raw_pinned_items) -> list:
        pinned_items = []
        for item in raw_pinned_items:
            pinned_item = {}
            pinned_item['title'] = item.find(class_="repo").get_text().strip()
            if item.find(class_="pinned-item-desc color-fg-muted text-small mt-2 mb-0"):
                pinned_item['description'] = item.find(class_="pinned-item-desc color-fg-muted text-small mt-2 mb-0").get_text().strip()
            if item.find(itemprop="programmingLanguage"):
                pinned_item['programming_language'] = item.find(itemprop="programmingLanguage").get_text().strip()

            counter = 0
            # Get stars and forks
            for popularity in item.find_all(class_="pinned-item-meta Link--muted"):
                if counter == 0:
                    pinned_item['stars'] = popularity.get_text().strip()
                    counter += 1
                else:
                    pinned_item['forks'] = popularity.get_text().strip()
                    counter = 0

            pinned_items.append(pinned_item)
        return pinned_items

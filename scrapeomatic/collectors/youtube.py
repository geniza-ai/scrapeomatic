from pprint import pprint

from bs4 import BeautifulSoup
from requests import HTTPError
from requests_html import HTMLSession

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, YOUTUBE_BASE_URL


class YouTube(Collector):

    def __init__(self, timeout=5, proxy=None):
        super().__init__(timeout, proxy)
        self.proxy = proxy
        self.timeout = timeout
        self.session = HTMLSession()

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
        x = soup.find_all("meta")
        pprint(x)
        return user_data

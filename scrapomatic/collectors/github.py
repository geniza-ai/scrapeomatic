from bs4 import BeautifulSoup
from requests import HTTPError
from fake_headers import Headers

from scrapomatic.collector import Collector
from scrapomatic.utils.constants import GITHUB_BASE_URL


class Github(Collector):

    def __init__(self, timeout=5, proxy=None):
        super().__init__(timeout, proxy)
        self.proxy = proxy
        self.timeout = timeout

    def collect(self, username: str) -> dict:
        """
        Collects information about a given user's github account
        :param username:
        :return:
        """
        headers = {}
        response = self.make_request(url=f"{GITHUB_BASE_URL}/{username}", headers=headers)
        if response.status_code != 200:
            raise HTTPError(f"Error retrieving profile for {username}.  Status Code: {response.status_code}")

        # Now parse the incoming data
        soup = BeautifulSoup(response.text, "html.parser")
        user_data = {}

        return ""

    @staticmethod
    def __build_headers() -> dict:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'github.com',
            'If - None - Match': 'W/"ed584c87c3fd45b6878f0ea5a259d6d1"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'User-Agent': Headers().generate()['User-Agent'],
        }

        """
        full_name = driver.find_element_by_css_selector("span.p-name.vcard-fullname.d-block.overflow-hidden")
        try:
            bio = driver.find_element_by_css_selector("div.p-note.user-profile-bio.mb-3.js-user-profile-bio.f4")
        except NoSuchElementException:
            bio = ""
        try:
            location = driver.find_element_by_css_selector("span.p-label")
        except NoSuchElementException:
            location = ""
        try:
            email = driver.find_element_by_css_selector("li[itemprop='email']")
        except NoSuchElementException:
            email = ""

        try:
            contributions = driver.find_element_by_css_selector(".js-yearly-contributions")
        except NoSuchElementException:
            contributions = ""
        profile_data = {
            'full_name': full_name.text,
            'bio': bio.text if type(bio) is not str else "",
            'location': location.text if type(location) is not str else "",
            "contributions": contributions.text.split(" ")[0] if type(contributions) is not str else ""
        }
        """


if __name__ == '__main__':
    github = Github()
    github.collect("cgivre")

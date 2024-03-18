from functools import lru_cache
from pprint import pprint

from playwright.sync_api import ProxySettings
import facebook_scraper as fs

from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT


class Facebook(Collector):

    def __init__(self, timeout=DEFAULT_TIMEOUT, proxy=None, cert_path=None):
        super().__init__(timeout, proxy, cert_path)
        self.proxy = proxy
        self.cert_path = cert_path
        self.timeout = float(timeout * 1000)

        if self.proxy is not None:
            proxy_dict = Collector.format_proxy(self.proxy)
            self.proxy_settings = ProxySettings(proxy_dict)

    @lru_cache
    def collect(self, username: str, max_posts: int = 20) -> dict:
        """

        Args:
            username:
            max_posts:

        Returns:

        """
        return fs.get_profile(username, timeout=self.timeout)

    @lru_cache
    def get_page_info(self, account_id: str) -> dict:
        return fs.get_page_info(account_id, timeout=self.timeout)


if __name__ == "__main__":
    fb = Facebook()
    pprint(fb.collect('Pewdiepie'))

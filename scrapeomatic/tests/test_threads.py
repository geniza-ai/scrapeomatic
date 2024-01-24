import unittest

from playwright.sync_api import TimeoutError as Playwright_Timeout

from scrapeomatic.collectors.threads import Threads


class TestThreadsScraper(unittest.TestCase):
    """
    This class tests the Threads scraper.
    """

    def test_basic_call(self):
        threads_scraper = Threads()
        results = threads_scraper.collect("bbc")
        self.assertIsNotNone(results)

    def test_no_user(self):
        threads_scraper = Threads()
        self.assertRaises(Playwright_Timeout, threads_scraper.collect, "asdfjkahsdjkfhaksdfhajsdhfkajdshf")

    def test_get_tweet(self):
        threads_scraper = Threads()
        results = threads_scraper.get_post("CuWykcKtfxf")
        self.assertIsNotNone(results)

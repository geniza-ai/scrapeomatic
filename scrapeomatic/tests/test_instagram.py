import os
import unittest

from requests import HTTPError

from scrapeomatic.collectors.instagram import Instagram

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


class TestInstagramScraper(unittest.TestCase):
    """
    This class tests the Instagram scraper.  Be sure to run these tests locally as they do not work
    on GitHub actions.
    """

    @unittest.skipIf(IN_GITHUB_ACTIONS, "Instagram tests fail on GitHub Actions.")
    def test_basic_call(self):
        instagram_scraper = Instagram()
        results = instagram_scraper.collect("emmachamberlain")
        self.assertIsNotNone(results)

    @unittest.skipIf(IN_GITHUB_ACTIONS, "Instagram tests fail on GitHub Actions.")
    def test_no_user(self):
        instagram_scraper = Instagram()
        self.assertRaises(HTTPError, instagram_scraper.collect, "asdfjkahsdjkfhaksdfhajsdhfkajdshf")

    def test_get_post(self):
        instagram_scraper = Instagram()
        instagram_scraper.get_post_metrics("BOTU6rJhShv")


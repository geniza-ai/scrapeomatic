import unittest

from requests import HTTPError

from scrapeomatic.collectors.instagram import Instagram


class TestInstagramScraper(unittest.TestCase):
    """
    This class tests the Instagram scraper.
    """

    def test_basic_call(self):
        instagram_scraper = Instagram()
        results = instagram_scraper.collect("emmachamberlain")
        self.assertIsNotNone(results)

    def test_no_user(self):
        instagram_scraper = Instagram()
        self.assertRaises(HTTPError, instagram_scraper.collect, "asdfjkahsdjkfhaksdfhajsdhfkajdshf")

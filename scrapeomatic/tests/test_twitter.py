import unittest

from requests import HTTPError

from scrapeomatic.collectors.twitter import Twitter


class TestTwitterScraper(unittest.TestCase):
    """
    This class tests the Twitter scraper.
    """

    def test_basic_call(self):
        twitter_scraper = Twitter()
        results = twitter_scraper.collect("DerekBieri")
        self.assertIsNotNone(results)

    def test_no_user(self):
        twitter_scraper = Twitter()
        self.assertRaises(HTTPError, twitter_scraper.collect, "asdfjkahsdjkfhaksdfhajsdhfkajdshf", False)

    def test_get_tweet(self):
        twitter_scraper = Twitter()
        results = twitter_scraper.get_tweet("https://twitter.com/TuckerCarlson/status/1700251942424109552")
        self.assertIsNotNone(results)

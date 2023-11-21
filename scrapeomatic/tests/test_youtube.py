import unittest

from pprint import pprint
from scrapeomatic.collectors.youtube import YouTube


class TestYouTubeScraper(unittest.TestCase):
    """
    This class tests the GitHub scraper.
    """

    def test_basic_call(self):
        youtube_scraper = YouTube()
        results = youtube_scraper.collect("smartereveryday")
        pprint(results)
        # self.assertIsNotNone(results)

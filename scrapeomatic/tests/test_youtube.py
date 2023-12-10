import unittest

from scrapeomatic.collectors.youtube import YouTube


class TestYouTubeScraper(unittest.TestCase):
    """
    This class tests the YouTube scraper.
    """

    def test_basic_call(self):
        youtube_scraper = YouTube()
        results = youtube_scraper.collect("ViceGripGarage")
        self.assertIsNotNone(results)

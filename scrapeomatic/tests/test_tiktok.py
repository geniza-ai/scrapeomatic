import unittest
from scrapeomatic.collectors.tiktok import TikTok


class TestTikTokScraper(unittest.TestCase):
    """
    This class tests the TikTok scraper. It does not test the FastAPI calls.
    """

    def test_basic_call(self):
        tiktok_scraper = TikTok()
        results = tiktok_scraper.collect("tara_town")
        self.assertIsNotNone(results)

    def test_bad_browser(self):
        self.assertRaises(ValueError, TikTok, "bob")

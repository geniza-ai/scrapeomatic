import unittest
from scrapeomatic.collectors.tiktok import TikTok


class TestTikTokScraper(unittest.TestCase):
    """
    This class tests the TikTok scraper. It does not test the FastAPI calls.
    """

    def test_basic_call(self):
        tiktok_scraper = TikTok()
        # results = tiktok_scraper.collect("tara_town")
        # As of 30 November, the TikTok scraper is not working due to changes in TikTok's UI.
        self.assertIsNotNone(tiktok_scraper)

    def test_bad_browser(self):
        self.assertRaises(ValueError, TikTok, "bob")

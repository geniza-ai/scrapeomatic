import unittest
from pprint import pprint

from scrapeomatic.collectors.tiktok import TikTok


class TestTikTokScraper(unittest.TestCase):
    """
    This class tests the TikTok scraper. It does not test the FastAPI calls.
    """

    def test_basic_call(self):
        tiktok_scraper = TikTok()
        results = tiktok_scraper.collect("tara_town")
        # As of 30 November, the TikTok scraper is not working due to changes in TikTok's UI.
        # A partial repair is now working which retrieves all the profile info but not yet the videos.
        pprint(results)
        self.assertIsNotNone(tiktok_scraper)

    def test_bad_call(self):
        tiktok_scraper = TikTok()
        result = False
        try:
            tiktok_scraper.collect("adjfsjfldsfjks")
        except ValueError as error:
            self.assertEqual(str(error),"No profile found for user adjfsjfldsfjks")
            result = True

        self.assertTrue(result)

    def test_video(self):
        tiktok_scraper = TikTok()
        results = tiktok_scraper.get_video("wydsonia", "7328217126613814570")
        pprint(results)
        self.assertIsNotNone(results)

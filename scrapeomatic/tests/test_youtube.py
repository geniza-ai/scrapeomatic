import unittest

from requests import HTTPError

from scrapeomatic.collectors.youtube import YouTube


class TestYouTubeScraper(unittest.TestCase):
    """
    This class tests the YouTube scraper.
    """

    def test_basic_call(self):
        youtube_scraper = YouTube()
        results = youtube_scraper.collect("ViceGripGarage")
        self.assertIsNotNone(results)

    def test_no_user(self):
        youtube_scraper = YouTube()
        self.assertRaises(HTTPError, youtube_scraper.collect, "asdfjkahsdjkfhaksdfhajsdhfkajdshf")

    def test_video(self):
        youtube_scraper = YouTube()
        results = youtube_scraper.get_video("6YgYXHrDiuk")
        self.assertIsNotNone(results)

import unittest

from pprint import pprint
from scrapeomatic.collectors.github import Github


class TestGitHubScraper(unittest.TestCase):
    """
    This class tests the GitHub scraper.
    """

    def test_basic_call(self):
        github_scraper = Github()
        results = github_scraper.collect("cgivre")
        pprint(results)
        self.assertIsNotNone(results)

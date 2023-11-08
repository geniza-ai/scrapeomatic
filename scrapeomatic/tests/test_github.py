import unittest

from pprint import pprint
<<<<<<< HEAD
from scrapeomatic.collectors.github import GitHub
=======
from scrapomatic.collectors.github import Github
>>>>>>> f2da9b7bcae1b51306c05f2b9f0e42f851c2ed16


class TestGitHubScraper(unittest.TestCase):
    """
    This class tests the GitHub scraper.
    """

    def test_basic_call(self):
        github_scraper = GitHub()
        results = github_scraper.collect("cgivre")
        pprint(results)
        self.assertIsNotNone(results)

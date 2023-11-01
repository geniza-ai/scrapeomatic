import unittest
from scrapomatic.collectors.facebook import Facebook
from instagram import Instagram
from github import Github
from pinterest import Pinterest
from reddit import Reddit
from twitter import Twitter
from quora import Quora
from medium import Medium
import warnings

def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)
    return do_test

class Tests_scrapers(unittest.TestCase):
    @ignore_warnings
    def test_facebook(self):
        profile_data = Facebook.scrap('despotovicme','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),3,"If length is less than output was not expected")
    @ignore_warnings
    def test_instagram(self):
        profile_data = Instagram.scrap('therock','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),6)
    @ignore_warnings
    def test_github(self):
        profile_data = Github.scrap('shaikhsajid1111','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),4)
    @ignore_warnings
    def test_pinterest(self):
        profile_data = Pinterest.scrap('ohjoy','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),12)
    @ignore_warnings
    def test_reddit(self):
        profile_data = Reddit.scrap('AcanthocephalaTime52','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),6)
    @ignore_warnings
    def test_twitter(self):
        profile_data = Twitter.scrap('asadowaisi','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),11)
    @ignore_warnings
    def test_quora(self):
        profile_data = Quora.scrap('John-Cate-2','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),11)
    @ignore_warnings
    def test_medium(self):
        profile_data = Medium.scrap('KeithSpencer','chrome')
        self.assertIsInstance(profile_data,dict)
        self.assertEqual(len(profile_data),6)
if __name__ == '__main__':
    unittest.main()
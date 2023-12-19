import abc
from functools import lru_cache

import pandas as pd
import requests


class Collector(metaclass=abc.ABCMeta):
    """
    This class is an interface for all the data collectors in scrape-o-matic.
    """

    def __init__(self, timeout: int, proxy: dict):
        self.proxy = proxy
        self.timeout = timeout

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
                hasattr(subclass, 'scrape') and
                callable(subclass.scrape) or NotImplemented
        )

    @abc.abstractmethod
    def collect(self, username: str) -> dict:
        """
        Base method for all platform collectors. This method will return a dictionary of all
        the data available from the given social media platform.
        :param username: The username for the account that you want information about.
        :return:  A dict of all the data returned.
        """
        raise NotImplementedError

    @lru_cache
    def collect_to_dataframe(self, username: str) -> pd.DataFrame:
        """
        Returns a pandas dataframe of the target user.
        :param username: The target username
        :return: A pandas DataFrame of the data from the desired user profile.
        """
        return pd.DataFrame(self.collect(username))

    def make_request(self, url, params=None, headers=None):
        """
        Utility method to make an HTTP request.
        :param url:
        :param params:
        :param headers:
        :return:
        """
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        if self.proxy:
            proxy_dict = {
                'http': f'http://{self.proxy}',
                'https': f'http://{self.proxy}'
            }
            return requests.get(url, headers=headers, timeout=self.timeout, params=params, proxies=proxy_dict)

        return requests.get(url, timeout=self.timeout, headers=headers, params=params)

import abc
import json
from functools import lru_cache

import pandas as pd
import requests


class Collector(metaclass=abc.ABCMeta):
    """
    This class is an interface for all the data collectors in scrape-o-matic.
    """

    def __init__(self, timeout: int, proxy: str, cert_path: str, use_session: bool = False):
        self.proxy = proxy
        self.cert_path = cert_path if cert_path is not None else True
        self.timeout = timeout
        self.use_session = use_session
        if use_session:
            self.session = requests.Session()

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

    @staticmethod
    def format_proxy(proxy_url: str) -> dict:
        return {
            'http': f'http://{proxy_url}',
            'https': f'http://{proxy_url}'
        }

    def make_request(self, url, params=None, headers=None):
        """
        Utility method to make an HTTP GET request.
        :param url:  The URL which we are requesting.
        :param params:  A dictionary of parameters to be added to the request
        :param headers:  A dictionary of headers to be added to the request.
        :return:  The results of the request.
        """
        if headers is None:
            headers = {}
        if params is None:
            params = {}

        proxy_dict = None
        if self.proxy:
            proxy_dict = Collector.format_proxy(self.proxy)
        if self.use_session:
            return self.session.get(url, timeout=self.timeout, headers=headers, params=params, proxies=proxy_dict, verify=self.cert_path)
        return requests.get(url, timeout=self.timeout, headers=headers, params=params, proxies=proxy_dict, verify=self.cert_path)

    @staticmethod
    def write_to_file(json_data, outfile_name) -> None:
        """
        Used for testing. Writes JSON objects to a file.
        Args:
            json_data: The object to be written to a file/
            outfile_name: The output file name

        Returns: Nothing...
        """
        with open(outfile_name, "w", encoding='utf-8') as outfile:
            json.dump(json_data, outfile, indent=4)

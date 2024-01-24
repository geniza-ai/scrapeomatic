import logging

from playwright.sync_api import Route
from selenium import webdriver

from scrapeomatic.utils.constants import PLAYWRIGHT_BLOCK_RESOURCE_TYPES, PLAYWRIGHT_BLOCK_RESOURCE_NAMES

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s', level=logging.INFO)


class AsyncUtils:

    @staticmethod
    def intercept_route(route: Route) -> None:
        """
        Method to exclude unnecessary routes including images, fonts etc.
        Args:
            route: The inbound route.
        """
        if route.request.resource_type in PLAYWRIGHT_BLOCK_RESOURCE_TYPES:
            logging.debug(f'blocking background resource {route.request} blocked type "{route.request.resource_type}"')
            return route.abort()
        if any(key in route.request.url for key in PLAYWRIGHT_BLOCK_RESOURCE_NAMES):
            logging.debug(f"blocking background resource {route.request} blocked name {route.request.url}")
            return route.abort()
        return route.continue_()

    @staticmethod
    def get_cookie_dict(driver: webdriver) -> dict:
        """
        Gets the cookies from Selenium webdriver and reformats them into a dictionary.
        Args:
            driver: The input webdriver object

        Returns: A dictionary of cookies.

        """
        all_cookies = driver.get_cookies()
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']

        return cookies_dict

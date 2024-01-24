import logging

from playwright.sync_api import Route

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

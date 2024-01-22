from selenium import webdriver


class AsyncUtils:
    @staticmethod
    def get_cookie_dict(driver: webdriver) -> dict:
        """
        Gets the cookies from Selenium webdriver and reformats them into a dictionary.
        Args:
            driver: The input webdriver object

        Returns: A dictionary of cookies.

        """
        all_cookies = driver.get_cookies();
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']

        return cookies_dict

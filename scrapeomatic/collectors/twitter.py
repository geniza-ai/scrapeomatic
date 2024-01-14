import logging
from functools import lru_cache

import jmespath
from playwright.sync_api import sync_playwright, TimeoutError, ProxySettings
from requests import HTTPError
from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, TWITTER_BASE_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none"
}


class Twitter(Collector):
    """
    Collector for Twitter.  Sourced from https://scrapfly.io/blog/how-to-scrape-twitter/.
    """
    def __init__(self, timeout=DEFAULT_TIMEOUT, proxy=None, cert_path=None):
        super().__init__(timeout, proxy, cert_path)
        self.proxy = proxy
        self.cert_path = cert_path
        self.timeout = float(timeout * 1000)

        if self.proxy is not None:
            self.proxy_settings = ProxySettings(proxy)

    def get_tweet(self, url: str) -> dict:
        """
        Scrape a single tweet page for Tweet thread e.g.:
        https://twitter.com/Scrapfly_dev/status/1667013143904567296
        Return parent tweet, reply tweets and recommended tweets
        """
        _xhr_calls = []

        def intercept_response(response):
            """capture all background requests and save them"""
            # we can extract details from background requests
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # enable background request intercepting:
            page.on("response", intercept_response)
            # go to url and wait for the page to load
            page.goto(url)
            page.wait_for_selector("[data-testid='tweet']")

            # find all tweet background requests:
            tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
            for xhr in tweet_calls:
                data = xhr.json()
                result = data['data']['tweetResult']['result']
                return self.parse_tweet(result)

    def parse_tweet(self, data: dict) -> dict:
        """Parse Twitter tweet JSON dataset for the most important fields"""
        result = jmespath.search(
            """{
            created_at: legacy.created_at,
            attached_urls: legacy.entities.urls[].expanded_url,
            attached_urls2: legacy.entities.url.urls[].expanded_url,
            attached_media: legacy.entities.media[].media_url_https,
            tagged_users: legacy.entities.user_mentions[].screen_name,
            tagged_hashtags: legacy.entities.hashtags[].text,
            favorite_count: legacy.favorite_count,
            bookmark_count: legacy.bookmark_count,
            quote_count: legacy.quote_count,
            reply_count: legacy.reply_count,
            retweet_count: legacy.retweet_count,
            quote_count: legacy.quote_count,
            text: legacy.full_text,
            is_quote: legacy.is_quote_status,
            is_retweet: legacy.retweeted,
            language: legacy.lang,
            user_id: legacy.user_id_str,
            id: legacy.id_str,
            conversation_id: legacy.conversation_id_str,
            source: source,
            views: views.count
        }""",
            data,
        )
        result["poll"] = {}
        poll_data = jmespath.search("card.legacy.binding_values", data) or []
        for poll_entry in poll_data:
            key, value = poll_entry["key"], poll_entry["value"]
            if "choice" in key:
                result["poll"][key] = value["string_value"]
            elif "end_datetime" in key:
                result["poll"]["end"] = value["string_value"]
            elif "last_updated_datetime" in key:
                result["poll"]["updated"] = value["string_value"]
            elif "counts_are_final" in key:
                result["poll"]["ended"] = value["boolean_value"]
            elif "duration_minutes" in key:
                result["poll"]["duration"] = value["string_value"]
        user_data = jmespath.search("core.user_results.result", data)
        if user_data:
            result["user"] = parse_user(user_data)
        return result

    @lru_cache
    def collect(self, username: str) -> dict:
        """
        This function collects metadata about a specific Twitter/X user.
        Args:
            username: The account name with or without the leading @.

        Returns: A dictionary of account metadata.

        """
        _xhr_calls = []

        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]

        final_url = f"{TWITTER_BASE_URL}{username}"

        def intercept_response(response):
            """capture all background requests and save them"""
            # We can extract details from background requests
            if response.request.resource_type == "xhr":
                _xhr_calls.append(response)
            return response

        with sync_playwright() as pw:
            browser = pw.firefox.launch(headless=True, timeout=self.timeout)

            context = browser.new_context(viewport={"width": 1920, "height": 1080},
                                          extra_http_headers=DEFAULT_HEADERS)
            page = context.new_page()

            # enable background request intercepting:
            page.on("response", intercept_response)
            # go to url and wait for the page to load
            page.goto(final_url)
            try:
                page.wait_for_selector("[data-testid='primaryColumn']")
            except TimeoutError as exc:
                error_message = f"Error retrieving Twitter profile. Your IP could be blocked or the profile could be private."
                logging.error(error_message)
                raise HTTPError(error_message) from exc

            # find all tweet background requests:
            tweet_calls = [f for f in _xhr_calls if "UserBy" in f.url]
            for xhr in tweet_calls:
                data = xhr.json()
                return data['data']['user']['result']


def main():
    t = Twitter()
    print(t.collect("FoxNews"))


if __name__ == "__main__":
    main()

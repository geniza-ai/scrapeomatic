import json
import logging
from functools import lru_cache
from typing import Dict

import jmespath
from playwright.sync_api import ProxySettings, sync_playwright
from parsel import Selector
from nested_lookup import nested_lookup
from scrapeomatic.collector import Collector
from scrapeomatic.utils.constants import DEFAULT_TIMEOUT, THREADS_BASE_URL

logging.basicConfig(format='%(asctime)s - %(process)d - %(levelname)s - %(message)s')


class Threads(Collector):

    def __init__(self, timeout=DEFAULT_TIMEOUT, proxy=None, cert_path=None):
        super().__init__(timeout, proxy, cert_path)
        self.proxy = proxy
        self.cert_path = cert_path
        self.timeout = float(timeout * 1000)

        if self.proxy is not None:
            proxy_dict = Collector.format_proxy(self.proxy)
            self.proxy_settings = ProxySettings(proxy_dict)
        else:
            self.proxy_settings = None

    @lru_cache
    def get_post(self, post_id: str) -> dict:
        """
        Retrieves post metadata from Threads.
        Args:
            post_id: The post id to retrieve.  You can find this in the post URL.

        Returns: A dictionary containing the post metadata.

        """
        with sync_playwright() as pw_browser:
            # start Playwright browser
            if self.proxy_settings is not None:
                browser = pw_browser.chromium.launch(timeout=self.timeout)
            else:
                browser = pw_browser.chromium.launch(timeout=self.timeout, proxy=self.proxy_settings)

            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # go to url and wait for the page to load
            url = f"{THREADS_BASE_URL}t/{post_id}"
            page.goto(url)
            # wait for page to finish loading
            page.wait_for_selector("[data-pressable-container=true]")
            # find all hidden datasets
            selector = Selector(page.content())
            hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
            # find datasets that contain threads data
            for hidden_dataset in hidden_datasets:
                # skip loading datasets that clearly don't contain threads data
                if '"ScheduledServerJS"' not in hidden_dataset:
                    continue
                if "thread_items" not in hidden_dataset:
                    continue
                data = json.loads(hidden_dataset)
                # datasets are heavily nested, use nested_lookup to find
                # the thread_items key for thread data
                thread_items = nested_lookup("thread_items", data)
                if not thread_items:
                    continue
                # use our jmespath parser to reduce the dataset to the most important fields
                threads = [Threads.__parse_thread(t) for thread in thread_items for t in thread]
                return {
                    # the first parsed thread is the main post:
                    "thread": threads[0],
                    # other threads are replies:
                    "replies": threads[1:],
                }
            raise ValueError("could not find thread data in page")

    @lru_cache()
    def collect(self, username: str) -> dict:
        """Scrape Threads profile and their recent posts from a given username"""
        with sync_playwright() as pw_browser:
            # start Playwright browser
            if self.proxy_settings is not None:
                browser = pw_browser.chromium.launch(timeout=self.timeout)
            else:
                browser = pw_browser.chromium.launch(timeout=self.timeout, proxy=self.proxy_settings)

            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            final_url = f"{THREADS_BASE_URL}@{username}"

            page.goto(final_url, timeout=self.timeout)
            # wait for page to finish loading
            page.wait_for_selector("[data-pressable-container=true]")
            selector = Selector(page.content())
        parsed = {
            "user": {},
            "threads": [],
        }
        # find all hidden datasets
        hidden_datasets = selector.css('script[type="application/json"][data-sjs]::text').getall()
        for hidden_dataset in hidden_datasets:
            # skip loading datasets that clearly don't contain threads data
            if '"ScheduledServerJS"' not in hidden_dataset:
                continue
            is_profile = 'follower_count' in hidden_dataset
            is_threads = 'thread_items' in hidden_dataset
            if not is_profile and not is_threads:
                continue
            data = json.loads(hidden_dataset)
            if is_profile:
                user_data = nested_lookup('user', data)
                parsed['user'] = Threads.__parse_profile(user_data[0])
            if is_threads:
                thread_items = nested_lookup('thread_items', data)
                threads = [
                    Threads.__parse_thread(t) for thread in thread_items for t in thread
                ]
                parsed['threads'].extend(threads)
        return parsed

    @staticmethod
    def __parse_thread(data: Dict) -> Dict:
        """Parse Twitter tweet JSON dataset for the most important fields"""
        result = jmespath.search(
            """{
            text: post.caption.text,
            published_on: post.taken_at,
            id: post.id,
            pk: post.pk,
            code: post.code,
            username: post.user.username,
            user_pic: post.user.profile_pic_url,
            user_verified: post.user.is_verified,
            user_pk: post.user.pk,
            user_id: post.user.id,
            has_audio: post.has_audio,
            reply_count: view_replies_cta_string,
            like_count: post.like_count,
            images: post.carousel_media[].image_versions2.candidates[1].url,
            image_count: post.carousel_media_count,
            videos: post.video_versions[].url
        }""",
            data,
        )
        result["videos"] = list(set(result["videos"] or []))
        if result["reply_count"] and isinstance(result["reply_count"], int):
            result["reply_count"] = int(result["reply_count"].split(" ")[0])
        result[
            "url"
        ] = f"{THREADS_BASE_URL}/@{result['username']}/post/{result['code']}"
        return result

    @staticmethod
    def __parse_profile(data: Dict) -> Dict:
        """Parse Threads profile JSON dataset for the most important fields"""
        result = jmespath.search(
            """{
            is_private: text_post_app_is_private,
            is_verified: is_verified,
            profile_pic: hd_profile_pic_versions[-1].url,
            username: username,
            full_name: full_name,
            bio: biography,
            bio_links: bio_links[].url,
            followers: follower_count
        }""",
            data,
        )
        result["url"] = f"{THREADS_BASE_URL}/@{result['username']}"
        return result

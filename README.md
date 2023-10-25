# Scrape-O-Matic: Utilities for Pulling Data From Social Media Platforms

Scrape-O-Matic is a collection of tools designed to easily pull data from popular social media platforms. As many of these platforms make it extremely difficult or impossible to pull public data from their platforms, 

Scrape-O-Matic only works with public profiles and does not require any tokens or authentication.

### Disclaimer:
These tools are provided for your personal use.  You may only use them in accordance with the respective platforms' terms of service and any applicable laws.  We accept no responsibility for misuse.

Scrap-o-Matic will work with the following platforms:

* [Instagram](#instagram)
* [TikTok](#tiktok)

## Usage:
Every platform inherits from a `collector` object which has a minimum of one method: `collect(username)`.  The collectors may have additional methods, but at a minimum, you can use the `collect` method to get a dump of all the available data from the platform.

## Instagram
To pull data from Instagram, simply create an Instagram object, then call the `collect(<username>)` method.

### Example Usage
```python
from scrapomatic.collectors.instagram import Instagram

user_name = "<username>"
instagram_scraper = Instagram()
results = instagram_scraper.collect(user_name)
```

### Additional Options:
In the constructor, you can specify two additional options:

* `proxy`: An address for a proxy server
* `timeout`:  A timeout value in seconds.  Defaults to 5 seconds.

## TikTok
To pull data from TikTok, simply create a TikTok object, then call the `collect(<username>)` method.

### Example Usage
```python
from scrapomatic.collectors.tiktok import TikTok

user_name = "<username>"
tiktok_scraper = TikTok()
results = tiktok_scraper.collect(user_name)
```

The TikTok collector uses Selenium and the Chrome or FireFox extensions.  These must be installed for this collector to work.
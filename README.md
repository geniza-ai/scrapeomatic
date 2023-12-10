# Scrape-O-Matic: Utilities for Pulling Data From Social Media Platforms

Scrape-O-Matic is a collection of tools designed to easily pull data from popular social media platforms. As many of these platforms make it extremely difficult or impossible to pull public data from their platforms, 

Scrape-O-Matic only works with public profiles and does not require any tokens or authentication.

### Disclaimer:
These tools are provided for your personal use and with no guarantee at all.  You may only use them in accordance with the respective platforms' terms of service and any applicable laws.  We accept no responsibility for misuse.

Scrap-o-Matic will work with the following platforms:

* [Github](#github)
* [Instagram](#instagram)
* [TikTok](#tiktok)
* [YouTube](#youtube)

## Usage:
Every platform inherits from a `collector` object which has a minimum of one method: `collect(username)`.  The collectors may have additional methods, but at a minimum, you can use the `collect` method to get a dump of all the available data from the platform.

Additionally, every collector has a `collect_to_dataframe` which will return the same information in a Pandas DataFrame.

## Github
To pull data from Github, simply create a Github object, then call the `collect(<username>)` method.

### Example Usage

```python
from scrapeomatic.collectors.github import GitHub

user_name = '<username>'
github_scraper = GitHub()
results = github_scraper.collect(user_name)
```

**Note:**  GitHub seems to have some security measures in place to prevent scraping email addresses from github repos. At present, we are not able to retrieve the user's email.


## Instagram
To pull data from Instagram, simply create an Instagram object, then call the `collect(<username>)` method.

### Example Usage

```python
from scrapeomatic.collectors.instagram import Instagram

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
from scrapeomatic.collectors.tiktok import TikTok

user_name = "<username>"
tiktok_scraper = TikTok()
results = tiktok_scraper.collect(user_name)
```

The TikTok collector uses Selenium and the Chrome or FireFox extensions.  These must be installed for this collector to work.

## YouTube
To pull data from YouTube, simply create a YouTube object, then call the `collect(<username>` method.

### Example Usage

```python
from scrapeomatic.collectors.youtube import YouTube

account = "<account handle>"
youtube_scraper = YouTube()
results = youtube_scraper.collect(account)
```


# Updates
Social Media platforms change their interfaces from time to time.  This table reflects when Scrape-O-Matic has last been tested.

| Platform | Last Updated Date |
|:---------|:------------------|
| GitHub | Nov 15, 2023      |
| Instagram | Nov 6, 2023       |
| TikTok | Nov 6, 2023       | 
| YouTube | Nov 30, 2023 |


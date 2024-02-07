# Scrape-O-Matic: Utilities for Pulling Data From Social Media Platforms

Scrape-O-Matic is a collection of tools designed to easily pull data from popular social media platforms. As many of these platforms make it extremely difficult or impossible to pull public data from their platforms, 

Scrape-O-Matic only works with public profiles and does not require any tokens or authentication.

### Caching
Scrape-O-Matic makes use of caching.  If you repeatedly scrape the same user account in the same process the response are cached to avoid being blocked.

### Disclaimer:
These tools are provided for your personal use and with no guarantee at all.  You may only use them in accordance with the respective platforms' terms of service and any applicable laws.  We accept no responsibility for misuse.  

#### Is Scraping Legal?
In general, scraping is legal if you are not logging into a website.  However, that does not mean that scraping is welcome by all the sites you wish to scrape.  I recommend using a proxy with rotating IP addresses to avoid being blocked by the various social media sites.  This does not constitute legal advice.

Scrap-o-Matic will work with the following platforms:

* [Github](#github)
* [Instagram](#instagram)
* [Threads](#threads)
* [TikTok](#tiktok)
* [Twitter/X](#twitter--x)
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

### Additional Methods:
The Instagram collector also features:

* `get_post(<post id>)`:  Returns metadata about a specific post.  The video ID you will need can be found in the Instagram URL for the video. For example: `https://www.instagram.com/p/CuE2WNQs6vH/`, the video id would be `CuE2WNQs6vH`.

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


## Threads
To pull metadata from Threads (https://www.threads.net), simply create a Threads object then call the `collect(<username>)` method.

## Other Methods:
You can retrieve an individual post along with all its associated metadata with the `get_post(<id>)` method.  You can get the post_id from the URL.  IE:  `https://threads.net/t/<id>`

## Example Usage

```python
from scrapeomatic.collectors.threads import Threads

user_name = "<username>"
threads_scraper = Threads()
profile_info = threads_scraper.collect(user_name)

post_id = "<post_id>"
post_info = threads_scraper.get_post(post_id)

```


## TikTok
To pull data from TikTok, simply create a TikTok object, then call the `collect(<username>)` method.

### Other Methods 
The TikTok collector also features a `get_video()` method which will retrieve all available metadata about a specific TikTok video.  You'll need the username of the author and the video id.  Both can be found in the URL for the video.
For example, if you wanted to collect the following video: `https://www.tiktok.com/@yincardify/video/7322915114292710699`, you could call `get_video('yincardify', '7322915114292710699')`


### Example Usage

```python
from scrapeomatic.collectors.tiktok import TikTok

user_name = "<username>"
tiktok_scraper = TikTok()
results = tiktok_scraper.collect(user_name)

# Get video info
video_data = tiktok_scraper.get_video('yincardify', '7322915114292710699')
```

The TikTok collector uses Selenium and the Chrome or FireFox extensions.  These must be installed for this collector to work.

## Twitter / X
To pull data from YouTube, simply create a Twitter object, then call the `collect(<username>)` method.  Twitter/X does not want you scraping their site and will very quickly block you if you are not careful.  To avoid being blocked, you must use some sort of proxy service which rotates the IP address of the requests.


### Getting the timeline:
Twitter makes it very difficult to pull the timeline of an individual user. However, you can do this with Scrape-O-Matic but the cost is a small delay in scraping.  The tweets associated with an individual profile come in a separate XHR call which takes a second or two to receive after the initial call.  If you are simply looking to get user profile set the `with_tweets` parameter to `False`.  The tweet_delay defaults to 2000ms.  You can reduce this but you may not always get the tweets in the profile.

The `collect()` method has two additional parameters:
* `with_tweets`:  A boolean variable which you can set if you do not want the tweets with the user profile
* `tweet_delay`:  The time delay in milliseconds for the scraper to wait before attempting to parse tweets.

### Example Usage

```python
from scrapeomatic.collectors.twitter import Twitter

account = "<account handle>"
twitter_scraper = Twitter()
results = twitter_scraper.collect(account)
```
### Other Methods:
In addition to getting user profiles, ScrapeOMatic can also retrieve metadata about a specific tweet using the `get_tweet()` method.  You must supply the complete URL for the tweet.

```python
from scrapeomatic.collectors.twitter import Twitter

account = "<account handle>"
twitter_scraper = Twitter()
results = twitter_scraper.get_tweet("https://twitter.com/JokesMemesFacts/status/1187906420248846342")

```

## YouTube
To pull data from YouTube, simply create a YouTube object, then call the `collect(<username>)` method.

### Example Usage

```python
from scrapeomatic.collectors.youtube import YouTube

account = "<account handle>"
youtube_scraper = YouTube()
results = youtube_scraper.collect(account)
```

### Additional Methods:
The YouTube collector also features:

* `get_video(<video id>)`:  Returns metadata about a specific video.  The video ID you will need can be found in the YouTube URL for the video. For example: `https://www.youtube.com/watch?v=6YgYXHrDiuk`, the video id would be `6YgYXHrDiuk`.

# Updates
Social Media platforms change their interfaces from time to time.  This table reflects when Scrape-O-Matic has last been tested.

| Platform | Last Updated Date |
|:---------|:------------------|
| GitHub | Nov 15, 2023      |
| Instagram | Nov 6, 2023       |
| Threads | Jan 24, 2024      | 
| TikTok | Feb 6, 2024       | 
| Twitter | Jan 14, 2024      |
| YouTube | Nov 30, 2023      |


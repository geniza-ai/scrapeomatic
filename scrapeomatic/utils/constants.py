PLAYWRIGHT_BLOCK_RESOURCE_TYPES = [
  'beacon',
  'csp_report',
  'font',
  'image',
  'imageset',
  'media',
  'object',
  'texttrack',
]

PLAYWRIGHT_BLOCK_RESOURCE_NAMES = [
  'adzerk',
  'analytics',
  'cdn.api.twitter',
  'doubleclick',
  'exelator',
  'facebook',
  'fontawesome',
  'google',
  'google-analytics',
  'googletagmanager',
]


DEFAULT_BROWSER = "chrome"
DEFAULT_TIMEOUT = 5
DEFAULT_VIDEO_LIMIT = 10
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
MAX_RETRIES = 5

# Base URLs
GITHUB_BASE_URL = "https://github.com"
INSTAGRAM_BASE_URL =  "https://www.instagram.com"
INSTAGRAM_QUERY_HASH = "b3055c01b4b222b8a47dc12b090e4e64"
INSTAGRAM_PROFILE_URL = f"{INSTAGRAM_BASE_URL}/api/v1/users/web_profile_info/"
INSTAGRAM_VIDEO_URL = f"{INSTAGRAM_BASE_URL}/graphql/query/?query_hash={INSTAGRAM_QUERY_HASH}&variables="
INSTAGRAM_APP_ID = "936619743392459"
THREADS_BASE_URL = "https://www.threads.net/"
TIKTOK_BASE_URL = "https://tiktok.com/@"
TWITTER_BASE_URL = "https://x.com/"
DEFAULT_TWEET_TIMEOUT = 2000
YOUTUBE_BASE_URL = "https://www.youtube.com/@"

"""Scrapy 全局配置"""

BOT_NAME = "tibetan_med_spider"
SPIDER_MODULES = ["tibetanMedResourceSpider.spiders"]
NEWSPIDER_MODULE = "tibetanMedResourceSpider.spiders"

ROBOTSTXT_OBEY = False

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

DOWNLOAD_TIMEOUT = 30
CONCURRENT_REQUESTS = 5
DOWNLOAD_DELAY = 0.3
RANDOMIZE_DOWNLOAD_DELAY = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# 默认输出：scrapy crawl nwipb 时写入 results/nwipb/nwipb_<时间戳>.json
FEEDS = {
    "results/nwipb/nwipb_%(time)s.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": 2,
        "ensure_ascii": False,
    }
}

ITEM_PIPELINES = {}

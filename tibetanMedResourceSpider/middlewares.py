"""Scrapy 中间件定义（标准模板）

当前项目未使用自定义中间件。本文件保留 Scrapy 标准模板结构，便于后续扩展。
"""

from scrapy import signals


class TibetanMedSpiderMiddleware:
    """爬虫中间件（Spider Middleware）"""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, request, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        return None

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class TibetanMedDownloaderMiddleware:
    """下载器中间件（Downloader Middleware）"""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        return None

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

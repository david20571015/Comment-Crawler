from typing import List
import urllib.parse

from crawler.crawler import BasicCrawler
from crawler.crawler import Crawler
from crawler.crawler import EmptyCrawler
from crawler.custom_crawler import EtTodayCrawler
from crawler.custom_crawler import LtnCrawler
from crawler.custom_crawler import StormCrawler, UdnCrawler

_EMPTY_CRAWLER_HOST = [
    'www.cna.com.tw',  # 中央社
]

_BASIC_CRAWLER_HOST = [
    'www.chinatimes.com',  # 中時
    'news.cts.com.tw',  # 華視
    'news.ebc.net.tw',  # 東森
    'tfc-taiwan.org.tw',  # 台灣事實查核中心
    'www.setn.com',  # 三立
]


def get_crawler(url: str) -> Crawler:
    """Returns the crawler for the given url.

    Args:
        url: The url of the page to crawl.

    Returns:
        The crawler for the given url.
    """
    host_name = urllib.parse.urlparse(url).netloc

    crawler: Crawler = BasicCrawler()

    if host_name in _EMPTY_CRAWLER_HOST:
        crawler = EmptyCrawler()
    elif host_name in _BASIC_CRAWLER_HOST:
        crawler = BasicCrawler()
    elif host_name == 'www.ettoday.net':
        crawler = EtTodayCrawler()
    elif host_name == 'news.ltn.com.tw':
        crawler = LtnCrawler()
    elif host_name in 'www.storm.mg':
        crawler = StormCrawler()
    elif host_name == 'udn.com':
        crawler = UdnCrawler()

    return crawler


def crawl(url: str, size: int = 20) -> List[str]:
    """Crawls the comments of a page.

    Args:
        url: The url of the page to crawl.
        size: The maximum number of comments to crawl.

    Returns:
        A list of comments.
    """
    crawler = get_crawler(url)
    return crawler.crawl(url, size)

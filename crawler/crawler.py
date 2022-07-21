import logging
from typing import List
import urllib.parse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def init_driver(chrome_version: str = '103.0.5060.53') -> WebDriver:
    """Initializes a webdriver.

    Args:
        chrome_version: The version of Chrome driver to use.

    Returns:
        A webdriver.
    """
    driver_manager = ChromeDriverManager(version=chrome_version)
    driver = webdriver.Chrome(service=Service(driver_manager.install()))
    return driver


def crawl_fb_comments(
    comment_url: str,
    driver: WebDriver,
    size: int = 20,
) -> List[str]:
    """Crawls the comments of a Facebook comment page.

    Args:
        comment_url: The url of the page to crawl.
        driver: The webdriver to use.
        size: The maximum number of comments to crawl.

    Returns:
        A list of comments.
    """
    driver.switch_to.new_window('tab')

    parsed_url = urllib.parse.urlparse(comment_url)._asdict()
    query = urllib.parse.parse_qs(parsed_url['query'])
    query['numposts'] = str(size)  # type: ignore
    parsed_url['query'] = urllib.parse.urlencode(query, doseq=True)

    query_url = urllib.parse.urlunparse(parsed_url.values())  # type: ignore

    logging.info('Crawling comments from %s.', query_url)
    driver.get(query_url)

    comment_elements = driver.find_elements(
        By.CSS_SELECTOR, 'div.UFIImageBlockContent.clearfix span._5mdd')
    comments = [ele.get_attribute('innerText') for ele in comment_elements]
    logging.info('Crawled %d comments from facebook.', len(comments))

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return comments[:size]


class Crawler():
    """Base class for crawlers.
    """

    def _preprocess(self, driver: WebDriver) -> None:
        """
        Preprocesses the page to be able to clawer the comments.
        """

    def _find_fb_comments_iframe(self, driver: WebDriver):
        fb_comments_locator = (
            By.CSS_SELECTOR,
            'iframe[data-testid="fb:comments Facebook Social Plugin"]')
        comment_iframe = WebDriverWait(driver, timeout=5).until(
            EC.presence_of_element_located(fb_comments_locator))

        return comment_iframe

    def crawl(self, url: str, size: int = 20) -> List[str]:
        """Crawls the comments of a page.

        Args:
            url: The url of the page to crawl.
            size: The maximum number of comments to crawl.

        Returns:
            A list of comments.
        """
        driver = init_driver()
        driver.get(url)

        self._preprocess(driver)

        try:
            comment_iframe = self._find_fb_comments_iframe(driver)
        except TimeoutException as err:
            print(err)
            return []

        comment_url = comment_iframe.get_attribute('src')
        comments = crawl_fb_comments(comment_url, driver, size)

        driver.quit()

        return comments[:size]


class BasicCrawler(Crawler):
    """Basic Crawler.

    This crawler is for the pages without preprocessing, and only
    crawl comments from the Facebook comments plugin.
    """


class EmptyCrawler(Crawler):
    """Empty Crawler.

    This crawler is for the pages without comments.
    """

    def crawl(self, url: str, size: int = 20) -> List[str]:
        """Crawls the comments of a page.

        Args:
            url: The url of the page to crawl.
            size: The maximum number of comments to crawl.

        Returns:
            An empty list.
        """
        return []

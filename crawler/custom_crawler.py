import logging
from typing import List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from crawler.crawler import crawl_fb_comments
from crawler.crawler import Crawler
from crawler.crawler import init_driver


class EtTodayCrawler(Crawler):
    """Crawler for `www.ettoday.net`."""

    def _find_ettoday_comments_iframe(self, driver: WebDriver):
        ettoday_comments_locator = (By.CSS_SELECTOR, 'div.et_board iframe')
        comment_iframe = WebDriverWait(driver, timeout=5).until(
            EC.presence_of_element_located(ettoday_comments_locator))

        return comment_iframe

    def _crawl_ettoday_comments(
        self,
        comment_url: str,
        driver: WebDriver,
        size: int = 20,
    ) -> List[str]:
        """Crawls the comments of a ETToday comments page.

        Args:
            comment_url: The url of the page to crawl.
            driver: The webdriver to use.
            size: The maximum number of comments to crawl.

        Returns:
            A list of comments.
        """
        driver.switch_to.new_window('tab')
        logging.info('Crawling comments from %s.', comment_url)
        driver.get(comment_url)

        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'p.summary')
        comments = [ele.text for ele in comment_elements]
        logging.info('Crawled %d comments from ettoday.', len(comments))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        return comments[:size]

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

        comments = []

        try:
            comment_iframe = self._find_fb_comments_iframe(driver)
            comment_url = comment_iframe.get_attribute('src')
            comments.extend(crawl_fb_comments(comment_url, driver, size))
        except TimeoutException as err:
            logging.error(err)

        try:
            comment_iframe = self._find_ettoday_comments_iframe(driver)
            comment_url = comment_iframe.get_attribute('src')
            comments.extend(
                self._crawl_ettoday_comments(comment_url, driver, size))
        except TimeoutException as err:
            logging.error(err)

        driver.quit()

        return comments[:size]


class LtnCrawler(Crawler):
    """Crawler for `news.ltn.com.tw`."""

    def _preprocess(self, driver: WebDriver) -> None:
        WebDriverWait(driver, timeout=5).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'div.softPush_notification button.softPush_refuse',
            ))).click()

        driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.END)


class StormCrawler(Crawler):
    """Crawler for `www.storm.mg`."""

    def _preprocess(self, driver: WebDriver) -> None:
        WebDriverWait(driver, timeout=5).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                'button#onesignal-slidedown-cancel-button',
            ))).click()


class UdnCrawler(Crawler):
    """Crawler for `udn.com`."""

    def _crawl_udn_comments(
        self,
        driver: WebDriver,
        size: int = 20,
    ) -> List[str]:
        """Crawls the comments of a UDN page.

        Args:
            comment_url: The url of the page to crawl.
            driver: The webdriver to use.
            size: The maximum number of comments to crawl.

        Returns:
            A list of comments.
        """

        comment_elements = driver.find_elements(
            By.CSS_SELECTOR,
            'section.discuss-board.article-section.context-box p')
        comments = [ele.text for ele in comment_elements]
        logging.info('Crawled %d comments from udn.', len(comments))

        return comments[:size]

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

        comments = []

        try:
            comment_iframe = self._find_fb_comments_iframe(driver)
            comment_url = comment_iframe.get_attribute('src')
            comments.extend(crawl_fb_comments(comment_url, driver, size))
        except TimeoutException as err:
            logging.error(err)

        comments.extend(self._crawl_udn_comments(driver, size))

        driver.quit()

        return comments[:size]

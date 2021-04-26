##Written by kelseykm

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging
from typing import Optional

#Create logging object
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.propagate = False
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Sabishare(object):
    """ Class for getting download links from saboshare """

    TIMEOUT = 5 #timeout for WebDriverWait

    def __init__(self) -> None:
        #create driver options
        logger.debug("Creating and adding webdriver options")
        self.option: selenium.webdriver.chrome.options.Options = webdriver.ChromeOptions()
        # self.option.headless = True ##too heavy on resources to run efficiently
        self.option.add_argument("--incognito")
        self.option.add_argument("--ignore-certificate-errors")
        self.option.add_experimental_option("prefs", {"download.prompt_for_download": True})

        #create driver
        logger.debug("Creating chrome webdriver")
        self.driver: selenium.webdriver.chrome.webdriver.WebDriver = webdriver.Chrome(options=self.option)

        #explicit wait
        logger.debug("Creating webdriver wait object")
        self.wait: selenium.webdriver.support.wait.WebDriverWait = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT)

    def get_download_link(self, url: str) -> Optional[str]:
        """ Get download link from sabishare """

        logger.debug("Getting url with driver")
        self.driver.get(url)

        #stop if video is not available
        if '404' in self.driver.title:
            logger.warning("URL page not found: %s", self.driver.current_url)
        else:
            try:
                logger.debug("Finding download button...")
                button = self.wait.until(
                    method=expected_conditions.presence_of_element_located((By.CLASS_NAME, 'download')),
                    message="Download button not found" #message returned if method fails
                    )
            except selenium.common.exceptions.TimeoutException as e:
                logger.error("%s", e)
            else:
                logger.debug("Clicking download button")
                button.click()

            try:
                logger.debug("Finding download link...")
                link_element = self.wait.until(
                    method=expected_conditions.presence_of_element_located((By.CLASS_NAME, 'download-url')),
                    message="Download link not found" #message returned of method fails
                )
            except selenium.common.exceptions.TimeoutException as e:
                logger.error("%s", e)
            else:
                logger.debug("Getting href from element")
                link = link_element.get_attribute('href') #get href from WebElement
                return link

    def close_driver(self) -> None:
        """ Close webdriver """
        logger.debug("Closing webdriver")
        self.driver.close()

class O2tvSeries(object):
    """ Class for getting download links from o2tvseries """

    TIMEOUT = 5 #timeout for WebDriverWait

    def __init__(self) -> None:
        #create driver options
        logger.debug("Creating and adding webdriver options")
        self.option: selenium.webdriver.chrome.options.Options = webdriver.ChromeOptions()
        self.option.add_argument("--incognito")
        self.option.add_argument("--ignore-certificate-errors")
        self.option.add_experimental_option("prefs", {"download.prompt_for_download": True})

        #create driver
        logger.debug("Creating chrome webdriver")
        self.driver: selenium.webdriver.chrome.webdriver.WebDriver = webdriver.Chrome(options=self.option)

        #explicit wait
        logger.debug("Creating webdriver wait object")
        self.wait: selenium.webdriver.support.wait.WebDriverWait = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT)

    def get_download_link(self, url: str) -> str:
        """ Get download link from o2tvseries """
        logger.debug("Getting url with driver")
        self.driver.get(url)

        logger.debug("Returning redirected url")
        return self.driver.current_url

    def close_driver(self) -> None:
        """ Close webdrive"""
        logger.debug("Closing webdriver")
        self.driver.close()

##Written by kelseykm

import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import logging

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
    TIMEOUT = 5 #timeout for WebDriverWait
    
    def __init__(self):
        #create driver options
        logger.debug("Creating and adding webdriver options")
        self.option = webdriver.ChromeOptions()
        # self.option.headless = True ##too heavy on resources to run efficiently
        self.option.add_argument("--incognito")
        self.option.add_argument("--ignore-certificate-errors")
        self.option.add_experimental_option("prefs", {"download.prompt_for_download": True})
        
        #create driver
        logger.debug("Creating chrome webdriver")
        self.driver = webdriver.Chrome(options=self.option)

        #explicit wait
        logger.debug("Creating webdriver wait object")
        self.wait = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT)
    
    def get_download_link(self, url):
        
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

    def close_driver(self):
        logger.debug("Closing webdriver")
        self.driver.close()

class O2tvSeries(object):
    TIMEOUT = 5 #timeout for WebDriverWait
    
    def __init__(self):
        #create driver options
        logger.debug("Creating and adding webdriver options")
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--incognito")
        self.option.add_argument("--ignore-certificate-errors")
        self.option.add_experimental_option("prefs", {"download.prompt_for_download": True})
        
        #create driver
        logger.debug("Creating chrome webdriver")
        self.driver = webdriver.Chrome(options=self.option)

        #explicit wait
        logger.debug("Creating webdriver wait object")
        self.wait = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT)
    
    def get_download_link(self, url):
        
        logger.debug("Getting url with driver")
        self.driver.get(url)
        
        logger.debug("Returning redirected url")
        return self.driver.current_url

    def close_driver(self):
        logger.debug("Closing webdriver")
        self.driver.close()

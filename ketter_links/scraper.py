##Written by kelseykm

import requests
from bs4 import BeautifulSoup
from . import drivers
import logging
import re


#create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.propagate = False
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_headers(netloc):
    logger.debug(f"Passing header to {netloc}")
    return {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                "Accept-Encoding": "gzip, deflate, br", 
                "Accept-Language": "en", 
                "Dnt": "1", 
                "Host": f"{netloc}",
                "Sec-Fetch-Dest": "document", 
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1", 
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }

class NetNaija(object):

    def __init__(self, parsed_url, text_pattern):
        self.parsed_url = parsed_url
        self.text_pattern = text_pattern
        self.url = parsed_url.geturl()

    def _get_download_links(self):
        
        # get the page code
        logger.debug("Creating requests session")
        with requests.Session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))
            
            with sess.get(self.url) as resp:
                logger.debug("Getting url content")
                data = resp.content

        # find all links matching the text_pattern regex
        logger.debug("Creating beautiful soup parser")
        soup = BeautifulSoup(data, "html.parser")
        logger.debug("Using beautiful soup object to find elements matching regex")
        elements = soup.find_all("a", text=self.text_pattern)

        if elements:
            # for each element in the ResultSet element, get the href and 
            # append download to avoid having to go to the final download page 
            links = []
            for link in elements:
                logger.debug("Getting href from beautiful soup element")
                l = link.get('href')
                links.append(l + "/download")

            if links:
                return links
        
        logger.warning("No elements match regex")

    def get_sabishare_links(self):
        #netnaija stores the videos at sabishare
        
        download_links = self._get_download_links()

        if download_links:
            logger.debug("Creating sabishare object")
            sabishare = drivers.Sabishare()

            sabishare_links = []
            for link in download_links:

                logger.debug("Getting download link from sabishare object")
                sabishare_link = sabishare.get_download_link(link)
                if sabishare_link:
                    sabishare_links.append(sabishare_link)
            
            logger.debug("Closing sabishare object driver")
            sabishare.close_driver()
            
            if sabishare_links:
                return sabishare_links

            logger.warning("No Sabishare links found")
            
        logger.warning("No download links available")

class LightDL(object):

    def __init__(self, parsed_url, text_pattern):
        self.parsed_url = parsed_url
        self.text_pattern = text_pattern
        self.url = parsed_url.geturl()

    def get_download_links(self):

        #get the page code
        logger.debug("Creating requests session")
        with requests.Session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            with sess.get(self.url) as resp:
                logger.debug("Getting url content")
                data = resp.content

        # find all links matching the text_pattern regex
        logger.debug("Creating beautiful soup parser")
        soup = BeautifulSoup(data, "html.parser")
        logger.debug("Using beautiful soup object to find elements matching regex")
        elements = soup.find_all("a", text=self.text_pattern)

        if elements:
            # for each element in the ResultSet element, get the href
            links = []
            for link in elements:
                logger.debug("Getting href from beautiful soup element")
                links.append(link.get('href'))

            if links:
                return links
        
        logger.warning("No elements match regex")

class O2tvSeries(object):

    def __init__(self, parsed_url, text_pattern):
        self.parsed_url = parsed_url
        self.text_pattern = text_pattern
        self.url = parsed_url.geturl()

    def get_download_links(self):
        logger.debug("Creating requests session")
        with requests.Session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            with sess.get(self.url) as resp:
                logger.debug("Getting url content")
                data = resp.content

                logger.debug("Creating beautiful soup parser")
                soup = BeautifulSoup(data, "html.parser")

                logger.debug("Using beautiful soup object to find pages elements")
                pages_element = soup.find("div", {"class": "pagination"})
                if pages_element:
                    pages = []
                    for child in pages_element.findChildren("a"):
                        child = child.get('href')
                        pages.append(child)
                else:
                    logger.warning("Could not find pages element")

                links = []

                logger.debug("Using beautiful soup object to find elements matching regex")
                elements = soup.find_all("a", text=self.text_pattern)
                if elements:
                    for element in elements:
                        logger.debug("Getting href from beautiful soup element")
                        links.append(element.get('href'))

            if pages:
                logger.debug("Getting links from the other pages")
                for page in pages:
                    with sess.get(page) as resp:
                        logger.debug("Getting url content")
                        data = resp.content

                    logger.debug("Creating beautiful soup parser")
                    soup = BeautifulSoup(data, "html.parser")
                    logger.debug("Using beautiful soup object to find elements matching regex")
                    elements = soup.find_all("a", text=self.text_pattern)

                    if elements:
                        for element in elements:
                            logger.debug("Getting href from beautiful soup element")
                            links.append(element.get('href'))

            download_links = []
            
            logger.debug("Getting download links")
            for link in links:
                with sess.get(link) as resp:
                    logger.debug("Getting url content")
                    data = resp.content

                logger.debug("Creating beautiful soup parser")
                soup = BeautifulSoup(data, "html.parser")
                dl_pattern = re.compile(r'^Click to Download Episode \d{2} in HD Mp4 Format$', re.IGNORECASE)
                logger.debug("Using beautiful soup object to find elements matching dl_pattern regex")
                element = soup.find("a", text=dl_pattern)

                if element:
                    logger.debug("Getting href from beautiful soup element")
                    download_links.append(element.get('href'))

            if download_links:
                return download_links

        logger.warning("No download links found")

    def solve_captcha_and_get_dl_links(self):
        links = self.get_download_links()

        if links:
            
            logger.debug("Creating drivers.O2tvSeries object")
            o2tv = drivers.O2tvSeries()
            
            final_download_links = []
            for link in links:
                logger.debug("Getting download link from o2tv object")
                fdl = o2tv.get_download_link(link)
                
                if fdl:
                    final_download_links.append(fdl)
                
            logger.debug("Closing o2tv object driver")
            o2tv.close_driver()

            if final_download_links:
                return final_download_links

            logger.warning("No final download links found after captcha")

        logger.warning("No links to follow to captcha")
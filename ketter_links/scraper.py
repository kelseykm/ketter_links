##Written by kelseykm

import requests
from bs4 import BeautifulSoup
from . import drivers
import logging
import re
from urllib.parse import ParseResult
from typing import Optional

#create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.propagate = False
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_headers(url_netloc: str) -> dict[str, str]:
    """ Generate headers to be used when making requests """
    logger.debug(f"Passing header to %s", url_netloc)
    return {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip",
                "Accept-Language": "en",
                "Dnt": "1",
                "Host": f"{url_netloc}",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }

class NetNaija:
    """ Class for scraping netnaija """

    def __init__(self, parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> None:
        self.parsed_url = parsed_url
        self.url: str = parsed_url.geturl()
        self.seasons_regex = seasons_regex
        self.episodes_regex = episodes_regex

    def _get_download_links(self) -> Optional[list[str]]:
        """ Get download links from netnaija """

        logger.debug("Creating requests session")
        with requests.Session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            #if season is not specified in url
            if not re.search(r'/season-\d', self.url):
                with sess.get(self.url) as resp:
                    data = resp.content

                soup = BeautifulSoup(data, "html.parser")
                text_pattern = re.compile(fr'^Season ({self.seasons_regex})$')
                elements = soup.find_all("a", text=text_pattern)
                season_links = []
                if elements:
                    for element in elements:
                        season_links.append(element.get('href'))

                episode_links = []

                for url in season_links:
                    #get episodes
                    with sess.get(url) as resp:
                        logger.debug("Getting url content")
                        data = resp.content

                    # find all links matching the text_pattern regex
                    logger.debug("Creating beautiful soup parser")
                    soup = BeautifulSoup(data, "html.parser")
                    logger.debug("Using beautiful soup object to find elements matching regex")
                    text_pattern = re.compile(fr'^Season \d Episode ({self.episodes_regex})$')
                    elements = soup.find_all("a", text=text_pattern)

                    if elements:
                        # for each element in the ResultSet element, get the href and
                        # append download to avoid having to go to the final download page
                        for link in elements:
                            logger.debug("Getting href from beautiful soup element")
                            l = link.get('href')
                            episode_links.append(l + "/download")

                if episode_links:
                    return episode_links

            #if season is specified in url
            else:
                #if episode is not specified in url
                if not re.search(r'episode-\d', self.url):
                    #get episodes
                    with sess.get(self.url) as resp:
                        logger.debug("Getting url content")
                        data = resp.content

                    # find all links matching the text_pattern regex
                    logger.debug("Creating beautiful soup parser")
                    soup = BeautifulSoup(data, "html.parser")
                    logger.debug("Using beautiful soup object to find elements matching regex")
                    text_pattern = re.compile(fr'^Season \d Episode ({self.episodes_regex})$')
                    elements = soup.find_all("a", text=text_pattern)

                    if elements:
                        # for each element in the ResultSet element, get the href and
                        # append download to avoid having to go to the final download page
                        episode_links = []
                        for link in elements:
                            logger.debug("Getting href from beautiful soup element")
                            l = link.get('href')
                            episode_links.append(l + "/download")

                        if episode_links:
                            return episode_links

                #if episode is specified in url
                elif re.search(r'episode-\d{1,6}/?$', self.url):
                    return [ self.url + "/download" if not self.url.endswith('/') else self.url + "download" ]

                #if final episode download link
                elif re.search(r'/download$', self.url):
                    return [ self.url ]

        logger.warning("%s - No elements match regex", self.__class__)

    def get_sabishare_links(self) -> Optional[list[str]]:
        """ Get download links from sabishare """
        #netnaija stores the videos at sabishare

        download_links = self._get_download_links()

        if download_links:
            #logger.debug("Creating sabishare object")
            #sabishare = drivers.Sabishare()

            sabishare_links = []
            for link in download_links:
                logger.debug("Creating sabishare object")
                sabishare = drivers.Sabishare()

                logger.debug("Getting download link from sabishare object")
                sabishare_link = sabishare.get_download_link(link)
                if sabishare_link:
                    sabishare_links.append(sabishare_link)

                logger.debug("Closing sabishare object driver")
                sabishare.close_driver()

            if sabishare_links:
                return sabishare_links

            logger.warning("No Sabishare links found")

        logger.warning("%s - No download links available", self.__class__)

class LightDL:
    """ Class for scraping lightdl """

    def __init__(self, parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> None:
        self.parsed_url = parsed_url
        self.url: str = parsed_url.geturl()
        self.seasons_regex = seasons_regex
        self.episodes_regex = episodes_regex

    def get_download_links(self) -> Optional[list[str]]:
        """ Get download links from lightdl """

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
        text_pattern = re.compile(fr's0?({self.seasons_regex})e0?({self.episodes_regex})', re.I)
        elements = soup.find_all("a", text=text_pattern)

        if elements:
            # for each element in the ResultSet element, get the href
            links = []
            for link in elements:
                logger.debug("Getting href from beautiful soup element")
                links.append(link.get('href'))

            if links:
                return links

        logger.warning("No elements match regex")

class O2tvSeries:
    """ Class for scraping o2tvseries """

    def __init__(self, parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> None:
        self.parsed_url = parsed_url
        self.url = parsed_url.geturl()
        self.seasons_regex = seasons_regex
        self.episodes_regex = episodes_regex

    def get_seasons(self, url: str, sess: requests.sessions.Session) -> Optional[list[str]]:
        """ Get season links """
        logger.debug("Getting seasons")

        with sess.get(url) as resp:
            logger.debug("Getting url content")
            data = resp.content

        logger.debug("Creating beautiful soup parser")
        soup = BeautifulSoup(data, "html.parser")

        text_pattern = re.compile(fr'^Season 0?({self.seasons_regex})$')

        logger.debug("Using beautiful soup object to find pages elements")
        elements = soup.find_all("a", text=text_pattern)
        season_links = []
        if elements:
            for element in elements:
                season_links.append(element.get('href'))

        if season_links:
            return season_links

        logger.warning("No season links found")

    def get_episodes(self, url: str, sess: requests.sessions.Session) -> Optional[list[str]]:
        """ Get season's episodes """
        logger.debug("Getting season's episodes")

        with sess.get(url) as resp:
            logger.debug("Getting url content")
            data = resp.content

        logger.debug("Creating beautiful soup parser")
        soup = BeautifulSoup(data, "html.parser")

        logger.debug("Using beautiful soup object to find pages elements")
        pages_element = soup.find("div", {"class": "pagination"})
        pages = []
        if pages_element:
            for child in pages_element.findChildren("a"):
                child = child.get('href')
                pages.append(child)
        else:
            logger.warning("Could not find pages element")

        episode_links = []

        logger.debug("Using beautiful soup object to find elements matching regex")
        text_pattern = re.compile(fr'^Episode 0?({self.episodes_regex})')
        elements = soup.find_all("a", text=text_pattern)
        if elements:
            for element in elements:
                logger.debug("Getting href from beautiful soup element")
                episode_links.append(element.get('href'))

        if pages:
            logger.debug("Getting links from the other pages")
            for page in pages:
                with sess.get(page) as resp:
                    logger.debug("Getting url content")
                    data = resp.content

                logger.debug("Creating beautiful soup parser")
                soup = BeautifulSoup(data, "html.parser")
                logger.debug("Using beautiful soup object to find elements matching regex")
                text_pattern = re.compile(fr'^Episode 0?({self.episodes_regex})')
                elements = soup.find_all("a", text=text_pattern)

                if elements:
                    for element in elements:
                        logger.debug("Getting href from beautiful soup element")
                        episode_links.append(element.get('href'))

        if episode_links:
            return episode_links

        logger.warning("No episode links found")

    def get_episode_quality_link(self, url: str, sess: requests.sessions.Session) -> Optional[str]:
        """ Get episode's quality download link """
        logger.debug("Getting episode's quality download link")

        with sess.get(url) as resp:
            logger.debug("Getting url content")
            data = resp.content

        logger.debug("Creating beautiful soup parser")
        soup = BeautifulSoup(data, "html.parser")

        dl_pattern = re.compile(
                r'^Click to Download Episode \d{1,6}(.+)? in HD Mp4 Format$',
                re.IGNORECASE
        )
        dl_pattern2 = re.compile(
                r'^Click to Download Episode \d{1,6}(.+)? in Mp4 Format$',
                re.IGNORECASE
        )

        logger.debug("Using beautiful soup object to find elements matching dl_pattern regex")
        element = soup.find("a", text=dl_pattern)
        if not element:
                element = soup.find("a", text=dl_pattern2)

        if element:
            logger.debug("Getting href from beautiful soup element")
            return element.get('href')

        logger.warning("No episode quality links found")

    def get_download_links(self) -> Optional[list[str]]:
        """ Get download links from o2tvseries """
        logger.debug("Creating requests session")
        with requests.Session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            #if no seasons are specified in url
            if not re.search(r'/season-\d', self.url, re.I):
                season_links = self.get_seasons(self.url, sess)
                if not season_links:
                    return

                combined_episode_links = []
                for se_link in season_links:
                    episode_links = self.get_episodes(se_link, sess)
                    if episode_links:
                        [ combined_episode_links.append(e_link) for e_link in episode_links ]
                if not combined_episode_links:
                    return

                download_links = []
                for ep_link in combined_episode_links:
                    episode_quality_link = self.get_episode_quality_link(ep_link, sess)
                    if episode_quality_link:
                        download_links.append(episode_quality_link)

                if download_links:
                    return download_links

            #if season is specified in url
            else:
                #if episode is not specified in url
                if not re.search(r'episode-\d', self.url, re.I):
                    episode_links = self.get_episodes(self.url, sess)
                    if not episode_links:
                        return

                    download_links = []
                    for ep_link in episode_links:
                        episode_quality_link = self.get_episode_quality_link(ep_link, sess)
                        if episode_quality_link:
                            download_links.append(episode_quality_link)

                    if download_links:
                        return download_links

                #if episode is specified in url
                elif re.search(r'episode-\d{1,6}', self.url, re.I):
                    return [self.get_episode_quality_link(self.url, sess)]

        logger.warning("%s - No download links found", self.__class__)

    def solve_captcha_and_get_dl_links(self) -> Optional[list[str]]:
        """ Solve solve captcha and get final download links """
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

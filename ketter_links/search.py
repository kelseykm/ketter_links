##Written by kelseykm

import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urlparse, ParseResult
from typing import Optional


#Set up logger
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
    logger.debug("Passing header to %s", url_netloc)
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
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            }

class NetNaija:
    """ Class for searching netnaija """

    # search url
    url = "https://www.thenetnaija.com/search"

    def __init__(self, search_string: str) -> None:
        self.search_string = search_string
        self.parsed_url: ParseResult = urlparse(self.url)

    def create_search_parameters(self) -> dict[str, str]:
        """ Create parameters to be passed with search url """
        logger.debug('Creating search parameters')
        return {
            't': f'{self.search_string}',
            'folder': 'videos',
        }

    def search(self) -> Optional[list[str]]:
        """ Send search request to netnaija and return results """

        logger.debug("Creating requests session")
        with requests.session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            logger.debug('Starting search')
            with sess.get(url=self.url, params=self.create_search_parameters()) as resp:
                logger.debug("Search url: %s", resp.url)
                data = resp.content

        logger.debug("Creating beautiful soup object")
        soup = BeautifulSoup(data, "html.parser")

        logger.debug("Using beautiful soup object to find results")
        results = soup.find_all("div", {'class': 'info'})

        if results:
            results_links = []

            for result in results:
                for res_link in result.findChildren("a"):
                    results_links.append(res_link.get('href'))

            return results_links

        logger.warning("No results found for %s", self.search_string)

    @property
    def safe_search_string(self) -> str:
        """ Escape regex special characters in search string """
        dangerous = {
            '\\', '.', '+', '?', '^', '$', '[', ']', '(', ')', '|'
            }
        safe_string = ''
        for character in self.search_string:
            if character in dangerous:
                safe_string += '\\'
            safe_string += character
        return safe_string

    def generate_search_regex_fields(self) -> dict[str, str]:
        """ Generate search regex fields """
        logger.debug("Generating search regex fields")

        fields = dict()

        logger.debug("Getting season if included in search string")
        season_pattern = re.compile(r'^(.+)(season \d{1,2})(.+)?$', re.I)
        season = season_pattern.search(self.search_string)
        if season:
            fields['season'] = re.sub(r'\s', '-', season.group(2))

        logger.debug("Getting episode if included in search string")
        episode_pattern = re.compile(r'^(.+)(episode \d{1,2})(.+)?', re.I)
        episode = episode_pattern.search(self.search_string)
        if episode:
            fields['episode'] = re.sub(r'\s', '-', episode.group(2))

        logger.debug("Getting series name")
        if season and episode:
            series_pattern = re.compile(r'^(.+) (season \d{1,2}) (episode \d{1,2})(.+)?$', re.I)
        elif season and not episode:
            series_pattern = re.compile(r'^(.+) (season \d{1,2})(.+)?$', re.I)
        elif not season and episode:
            series_pattern = re.compile(r'^(.+) (episode \d{1,2})(.+)?', re.I)
        else:
            series_pattern = re.compile(fr'({self.safe_search_string})', re.I)

        series = series_pattern.search(self.search_string)
        if series:
            fields['series'] = re.sub(r'\s', '-', series.group(1))

        return fields

    def get_links_from_results(self) -> Optional[set[str]]:
        """ Get links from search results """
        results = self.search()
        if results:
            fields = self.generate_search_regex_fields()
            links = set()
            logger.debug("Getting links from results")
            for result in results:
                if 'season' in fields and 'episode' in fields:
                    link = re.search(fr"(.+{fields['series']}/{fields['season']}/{fields['episode']})", result, re.I)
                    if link:
                        links.add(link.group(0))

                elif 'season' in fields:
                    link = re.search(fr"(.+{fields['series']}/{fields['season']})(.+)?", result, re.I)
                    if link:
                        links.add(link.group(1))

                else:
                    link = re.search(fr"(.+{fields['series']})/(.+)", result, re.I)
                    if link:
                        links.add(link.group(1))

            if links:
                return links

            logger.warning("%s - No matching results for %s", self.__class__, self.search_string)

        else:
            logger.warning("%s - No results to get links from", self.__class__)

class LightDl:
    """ Class for searching lightdl """

    # search url
    url = "https://www.lightdl.xyz/search"

    def __init__(self, search_string: str) -> None:
        self.search_string = search_string
        self.parsed_url: ParseResult = urlparse(self.url)

    def create_search_parameters(self, search_string: str) -> dict[str, str]:
        """ Create parameters to be passed with search url """
        logger.debug('Creating search parameters')
        return {
            'q': search_string,
        }

    def safe_search_string(self, search_string: str = None) -> str:
        """ Escape regex special characters in string """
        logger.debug('Creating safe search string')
        dangerous = {
            '\\', '.', '+', '?', '^', '$', '[', ']', '(', ')', '|'
            }
        safe_string = ''
        if search_string is None:
            search_string = self.search_string
        elif type(search_string) is not str:
            logger.warn("Something that wasn't a string was passed in to %s", self.safe_search_string)
            search_string = self.search_string

        for character in search_string:
            if character in dangerous:
                safe_string += '\\'
            safe_string += character
        return safe_string

    def generate_search_regex_fields(self) -> dict[str, str]:
        """ Generate search regex fields """
        logger.debug("Generating search regex fields")

        fields = dict()

        logger.debug("Getting season if included in search string")
        season_pattern = re.compile(r'^(.+)(season \d{1,2})(.+)?$', re.I)
        season = season_pattern.search(self.search_string)
        if season:
            fields['season'] = season.group(2)

        logger.debug("Getting episode if included in search string")
        episode_pattern = re.compile(r'^(.+)(episode \d{1,2})(.+)?', re.I)
        episode = episode_pattern.search(self.search_string)
        if episode:
            fields['episode'] = episode.group(2)

        logger.debug("Getting series name")
        if season and episode:
            series_pattern = re.compile(r'^(.+) (season \d{1,2}) (episode \d{1,2})(.+)?$', re.I)
        elif season and not episode:
            series_pattern = re.compile(r'^(.+) (season \d{1,2})(.+)?$', re.I)
        elif not season and episode:
            series_pattern = re.compile(r'^(.+) (episode \d{1,2})(.+)?', re.I)
        else:
            series_pattern = re.compile(fr'({self.safe_search_string()})', re.I)

        series = series_pattern.search(self.search_string)
        if series:
            fields['series'] = series.group(1)

        return fields

    def search(self) -> Optional[set[str]]:
        """ Send search request to lightdl and return parsed results """
        fields = self.generate_search_regex_fields()

        logger.debug("Creating requests session")
        with requests.session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            logger.debug('Starting search')
            with sess.get(url=self.url, params=self.create_search_parameters(fields['series'])) as resp:
                logger.debug("Search url: %s", resp.url)
                data = resp.content

        logger.debug("Creating beautiful soup object")
        soup = BeautifulSoup(data, "html.parser")

        logger.debug("Using beautiful soup object to find results")

        text_pattern = re.compile(fr"^(\s)?({self.safe_search_string(fields['series'])})(\s)?$", re.I)

        post_bodies = soup.find_all("h3")
        if post_bodies:
            results = set()
            for element in post_bodies:
                result = element.findChild("a", { 'title': text_pattern })
                if result:
                    results.add(result)

            links = set()
            if results:
                for result in results:
                    link = result.get('href')
                    links.add(link)

            if links:
                return links

        logger.warning("%s - No results found for %s", self.__class__, fields['series'])

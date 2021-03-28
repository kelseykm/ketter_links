##Written by kelseykm

import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urlparse


#Set up logger
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
    url = "https://www.thenetnaija.com/search"

    def __init__(self, search_string):
        self.search_string = search_string
        self.parsed_url = urlparse(self.url)

    def create_search_parameters(self):
        logger.debug('Creating search parameters')
       
        return {
            't': f'{self.search_string}',
            'folder': 'videos',
        }

    def search(self):
        
        logger.debug("Creating requests session") 
        with requests.session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            logger.debug('Starting search')
            with sess.get(url=self.url, params=self.create_search_parameters()) as resp:
                data = resp.content

        logger.debug("Creating beautiful soup object")
        soup = BeautifulSoup(data, "html5lib")

        logger.debug("Using beautiful soup object to find results")
        results = soup.find_all("h3", {'class': 'result-title'})

        if results:
            results_links = []

            for result in results:
                for res_link in result.findChildren("a"):
                    results_links.append(res_link.get('href'))

            return results_links
        
        logger.warning("No results found for %s", self.search_string)

    @property
    def safe_search_string(self):
        dangerous = {
            '\\', '.', '+', '?', '^', '$', '[', ']', '(', ')', '|'
            }
        
        safe_string = ''
        
        for ch in self.search_string:
            if ch in dangerous:
                safe_string += '\\'
            
            safe_string += ch

        return safe_string

    def generate_search_regex_fields(self):
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

    def get_links_from_results(self):
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

class LightDl(object):
    url = "https://www.lightdl.xyz/search"

    def __init__(self, search_string):
        self.search_string = search_string
        self.parsed_url = urlparse(self.url)

    def create_search_parameters(self, search_string):
        logger.debug('Creating search parameters')
       
        return {
            'q': search_string,
        }

    def safe_search_string(self, search_string=None):
        dangerous = {
            '\\', '.', '+', '?', '^', '$', '[', ']', '(', ')', '|'
            }
       
        safe_string = ''
        
        if not search_string:
            search_string = self.search_string
        
        for ch in search_string:
            if ch in dangerous:
                safe_string += '\\'
            
            safe_string += ch
        
        return safe_string

    def generate_search_regex_fields(self):
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

    def search(self):
        fields = self.generate_search_regex_fields()

        logger.debug("Creating requests session") 
        with requests.session() as sess:
            logger.debug("Updating session headers")
            sess.headers.update(get_headers(self.parsed_url.netloc))

            logger.debug('Starting search')
            with sess.get(url=self.url, params=self.create_search_parameters(fields['series'])) as resp:
                data = resp.content

        logger.debug("Creating beautiful soup object")
        soup = BeautifulSoup(data, "html5lib")

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

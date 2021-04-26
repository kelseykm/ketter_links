#!/usr/bin/env python3

##Written by kelseykm

from ketter_links import scraper, drivers, search, exceptions
import re
from urllib.parse import urlparse, ParseResult
import logging
import argparse
import sys
import string
from typing import Callable, Union, Optional

#set up logging
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
# logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
# handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


class scrapeSites:
    """ Class with methods for scraping all implemented sites """

    @staticmethod
    def o2tvseries(parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> Optional[list[str]]:
        """ O2tvSeries scraper """
        logger.debug("Started o2tvseries scraper")

        o2tvseries = scraper.O2tvSeries(parsed_url, seasons_regex, episodes_regex)
        return o2tvseries.solve_captcha_and_get_dl_links()

    @staticmethod
    def lightdl(parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> Optional[list[str]]:
        """ LightDL scraper """
        logger.debug("Started lightdl scraper")

        lightdl = scraper.LightDL(parsed_url, seasons_regex, episodes_regex)
        return lightdl.get_download_links()

    @staticmethod
    def netnaija(parsed_url: ParseResult, seasons_regex: str, episodes_regex: str) -> Optional[list[str]]:
        """ NetNaija scraper """
        logger.debug("Started netnaija scraper")

        net_naija = scraper.NetNaija(parsed_url, seasons_regex, episodes_regex)
        return net_naija.get_sabishare_links()

class searchSites:
    """ Class with methods for searching all implemented sites """

    @staticmethod
    def netnaija(search_string: str) -> Optional[set[str]]:
        """ NetNaija searcher """
        logger.debug("Started netnaija searcher")

        netnaija = search.NetNaija(search_string=search_string)
        return netnaija.get_links_from_results()

    @staticmethod
    def lightdl(search_string: str) -> Optional[set[str]]:
        """ LightDL searcher """
        logger.debug("Started netnaija searcher")

        lightdl = search.LightDl(search_string=search_string)
        return lightdl.search()

# Scraping functions
def grab_scrape_info() -> dict[str, Union[ParseResult, str]]:
    """ Grab information passed through command-line arguments """

    logger.debug("Grabbing scrape info from arguments")
    url: ParseResult = urlparse(args.url)
    if not url.scheme:
        logger.error("URL has no scheme")
        raise exceptions.InvalidInput('URL is incomplete. It has no scheme.')

    argument: Optional[str]
    for argument in args.seasons, args.episodes:
        if argument is not None:
            if len(argument) > 2 and not argument.startswith('['):
                logger.error("Invalid input format for seasons or episodes")
                raise exceptions.InvalidInput('Invalid input format for seasons or episodes')

            for argument_content in argument:
                if not argument_content in ''.join(['[', ']', ',', '-', ' ', string.digits]):
                    logger.error("Invalid input format for seasons or episodes")
                    raise exceptions.InvalidInput('Invalid input format for seasons or episodes')

    return {
        'url': url,
        'seasons': args.seasons,
        'episodes': args.episodes,
    }

def run_scrape(url: ParseResult, seasons_regex: str, episodes_regex: str) -> Optional[list[str]]:
    """ Run the actual scraping funtions """

    supported_sites: dict[str, Callable[ParseResult, str], Optional[list[str]]]
    supported_sites = {
        'www.thenetnaija.com': scrapeSites.netnaija,
        'www.lightdl.xyz': scrapeSites.lightdl,
        'o2tvseries.com': scrapeSites.o2tvseries,
    }
    if url.netloc not in supported_sites:
        logger.error("Website from url not implemented")
        raise exceptions.UnimplementedSite('Getting download links from that site is not yet implimented')

    return supported_sites[url.netloc](url, seasons_regex, episodes_regex)

def parse_scrape_info(scrape_info: str) -> str:
    """ Parses info passed into seasons/episodes commmand-line arguments """

    logger.debug("Parsing scrape info")
    separated = set()

    if scrape_info.strip().isdigit():
        separated.add(scrape_info.strip())

    else:
        scrape_info = scrape_info.strip()
        scrape_info = scrape_info.lstrip('[').rstrip(']')
        scrape_info = scrape_info.split(',')
        for info in scrape_info:
            if '[' in info or ']' in info:
                    logger.error("Invalid input format for seasons or episodes")
                    raise exceptions.InvalidInput('Invalid input format for seasons or episodes')

            if '-' in info:
                first, last = info.split('-')
                first = int(first.strip()); last = int(last.strip())
                list(separated.add(str(season_episode_number)) for season_episode_number in range(first, last + 1))
            elif info.strip().isdigit():
                separated.add(info.strip())

    if separated:
        return '|'.join(separated)

    logger.warning("No valid input for seasons or episodes")
    raise exceptions.InvalidInput("No valid input for seasons or episodes")

def construct_scrape_regex_patterns(scrape_info: dict[str, Union[ParseResult, str]]) -> dict[str, Union[ParseResult, str]]:
    """ Construct regex patterns for seasons/episodes """

    logger.debug("Constructing scrape regexes")
    for info in scrape_info:
        if info == 'url':
            continue

        if info == 'seasons':
            if scrape_info[info] is not None:
                if re.search(r'/season-\d{1,6}', scrape_info['url'].geturl()):
                    logger.warning("Season already specified in url")
                    raise exceptions.InvalidInput("Season already specified in url")

                scrape_info['seasons'] = parse_scrape_info(scrape_info[info])
            else:
                s = re.search(r'/season-(\d{1,6})', scrape_info['url'].geturl())
                if s:
                    scrape_info['seasons'] = s.group(1)
                else:
                    scrape_info['seasons'] = r'\d{1,6}'

        if info == 'episodes':
            if scrape_info[info] is not None:
                if re.search(r'/episode-\d{1,6}', scrape_info['url'].geturl()):
                    logger.warning("Episode already specified in url")
                    raise exceptions.InvalidInput("Episode already specified in url")

                scrape_info['episodes'] = parse_scrape_info(scrape_info[info])
            else:
                e = re.search(r'/episode-(\d{1,6})', scrape_info['url'].geturl())
                if e:
                    scrape_info['episodes'] = e.group(1)
                else:
                    scrape_info['episodes'] = r'\d{1,6}'

    return scrape_info

def scrape_main() -> None:
    """ Main function for scrape """

    logger.info("Starting scrape")
    search_info = construct_scrape_regex_patterns(grab_scrape_info())
    links = run_scrape(
        url=search_info['url'],
        seasons_regex=search_info['seasons'],
        episodes_regex=search_info['episodes']
    )
    if links:
        logger.debug("Writing urls to file")
        with open('urls.txt', 'w') as f:
            for link in links:
                f.write(link + '\n')
    else:
        logger.warning("No links available")

# Searching functions
def grab_search_info() -> dict[str,str]:
    """ Grab information passed through command-line arguments and modify it """
    logger.debug("Grabbing search info from arguments")

    if (args.season is not None and not args.season.isdigit()) or (args.episode is not None and not args.episode.isdigit()):
        logger.error("Invalid input format for seasons or episodes")
        raise exceptions.InvalidInput('Invalid input format for seasons or episodes')

    return {
        'series': args.series,
        'season': 'season ' + args.season if args.season else args.season,
        'episode': 'episode ' + args.episode if args.episode else args.episode,
    }

def run_search(search_info: dict[str, str]) -> dict[str, Optional[set[str]]]:
    """ Run the actual searching funtions """
    results = dict()

    func: Callable[[str], Optional[set[str]]]
    for func in searchSites.netnaija, searchSites.lightdl:
        if not search_info['season']:
            results[func.__name__] = func(
                search_info['series']
            )
        elif search_info['season'] and search_info['episode']:
            results[func.__name__] = func(
                ' '.join([search_info['series'], search_info['season'], search_info['episode']])
            )
        else:
            results[func.__name__] = func(
                ' '.join([search_info['series'], search_info['season']])
            )

    return results

def search_main() -> None:
    """ Main function for search """

    logger.info("Starting search")
    links = run_search(grab_search_info())
    if links:
        logger.info("Printing links")
        for key in links:
            print(f"{key.upper()}: {links[key]}")


if __name__ == "__main__":
    #Create argument parser
    logger.debug("Creating argument parser")
    parser = argparse.ArgumentParser()

    #Create subparsers
    sub_parser = parser.add_subparsers(title='Sub-commands', description='You may run --help on either of the following valid subcommands: scrape, search.')

    scrape_parser = sub_parser.add_parser('scrape')
    scrape_parser.add_argument('--url', help='The url of the series to scrape links for', required=True)
    scrape_parser.add_argument('--seasons', help='''
        The season(s) of the series to scrape links for. If the url provided is already for a
        specific season, skip this argument. If you want the links for just one season, put the
        number of the season e.g., '1', but if you want a range of seasons, put the range,
        surrounded by square brackets, e.g., '[3-7]'. If you want seasons that do not follow each
        other, put commas between them and surround them with square brackets, e.g., '[1,4,9]'. You
        may also combine the two methods, e.g., [4,9-11].
        If skipped and season was not specified in url, default is to get all seasons.
        ''',
        required=False)
    scrape_parser.add_argument('--episodes', help='''
        The episode(s) of the season(s) of the series to scrape links for. If the url provided is
        already for a specific episode of a specific season, skip this argument. If you want the
        links for just one episode of the season(s) specified, put the number of the episode e.g.,
        '1', but if you want a range of episodes, put the range, surrounded by square brackets, e.g.
        , '[3-7]'. If you want episodes that do not follow each other, put commas between them and
        surround them with square brackets, e.g., '[1,4,9]'. You may also combine the two methods,
        e.g., [4,9-11].
        If skipped and episode was not specified in url, default is to get all episodes.
        ''',
        required=False)
    scrape_parser.set_defaults(func=scrape_main)

    search_parser = sub_parser.add_parser('search')
    search_parser.add_argument('--series', help='The name of the series to search for', required=True)
    search_parser.add_argument('--season', help='''
        The season of the series to search for, e.g., "--season 4"
        ''',
        required=False)
    search_parser.add_argument('--episode', help='''
        The episode of the season of the series to search for, e.g. "--episode 5"
        ''',
        required=False)
    search_parser.set_defaults(func=search_main)

    #Print help and exit if no command-line arguments are supplied
    if len(sys.argv) < 2:
        logger.error("No arguments supplied")
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()

    #run main func
    args.func()

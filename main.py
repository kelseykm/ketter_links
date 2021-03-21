#!/usr/bin/env python3

##Written by kelseykm

from ketter_links import scraper, drivers
import re
from urllib.parse import urlparse
import logging, logging.config
import argparse

class Sites(object):
    @staticmethod
    def o2tvseries(parsed_url, regex):
        logger.debug("Started o2tvseries scraper")

        o2tvseries = scraper.O2tvSeries(parsed_url=parsed_url, text_pattern=regex)
        return o2tvseries.solve_captcha_and_get_dl_links()

    @staticmethod
    def lightdl(parsed_url, regex):
        logger.debug("Started lightdl scraper")

        lightdl = scraper.LightDL(parsed_url=parsed_url, text_pattern=regex)
        return lightdl.get_download_links()

    @staticmethod
    def netnaija(parsed_url, regex):
        logger.debug("Started netnaija scraper")

        net_naija = scraper.NetNaija(parsed_url=parsed_url, text_pattern=regex)
        return net_naija.get_sabishare_links()


def grab_info():
    url = urlparse(args.url)
    if not url.scheme:
        logger.error("URL has no scheme")
        raise Exception('URL is incomplete. It has no scheme.')
    
    regex = re.compile(fr'{args.regex}', re.IGNORECASE)

    return url, regex
    

def run(url, regex):
    supported_sites = {
        'www.thenetnaija.com': Sites.netnaija,
        'www.lightdl.xyz': Sites.lightdl,
        'o2tvseries.com': Sites.o2tvseries,
    }
    if url.netloc not in supported_sites:
        logger.error("Website from url not implemented")
        raise Exception('Getting download links from that site is not yet implimented')

    return supported_sites[url.netloc](url, regex)

def main():
    
    logger.info("Starting program")

    links = run(*grab_info())

    if links:
        logger.info("Writing urls to file")
    
        with open('urls.txt', 'w') as f:
            for link in links:
                f.write(link + '\n')
    
    else:
        logger.warning("No links available")


if __name__ == "__main__":
    
    #Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The url of the series to download")
    parser.add_argument("regex", help="The regular expression of the text of the episode links")
    args = parser.parse_args()

    #set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    #run main func
    main()

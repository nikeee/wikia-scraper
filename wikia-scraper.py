#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
#
#  Name:        wikia-scraper.py
#  Author:      James H. Loving, github.com/jameshloving
#  License:     See LICENSE file.
#  Description: This script will scrape a Wikia fan-Wiki and create a word list
#               for use in dictionary attacks.
#  Usage:       wikia-scraper.py --url URL --out OUTFILE
#  Example:     wikia-scraper.py --url https://starwars.wikia.com \
#                                --out out.txt
#
###############################################################################

import argparse
import sys
import _thread

import requests
import validators

from bs4 import BeautifulSoup
from halo import Halo

def GetSoup(url):
    response = requests.get(url)
    data = response.text
    return BeautifulSoup(data, 'lxml')


def GetLinks(table):
    links = set()

    for child in table.findChildren():
        for link in child.find_all('a', href=True):
            links.add((link['href']))

    return links


def GetClargs():
    parser = argparse.ArgumentParser(description='Parse a Wikia to produce a word list of article titles.')

    parser.add_argument('--url',
                        help='parse this Wikia URL, ex: "http://starwars.wikia.com/"',
                    )
    parser.add_argument('--out',
                        type=argparse.FileType('w'),
                        help='output results to this file',
                    )

    clargs = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    return clargs


def main():
    args = GetClargs()

    if not validators.url(args.url):
        print('Invalid URL. This may be due to lack of "http://" prefix.')

    spinner = Halo(text='Fetching chunked list of articles...')
    spinner.start()

    soup = GetSoup(args.url + '/wiki/Special:AllPages')

    spinner.succeed(text='Fetching chunked list of articles... Done!')

    chunks = set()
    articles = set()

    # get first list of chunks
    spinner = Halo(text='Processing chunks...')
    spinner.start()

    table_of_chunks = soup.find('table', {
        'class': ['allpageslist', 'mw-allpages-table-chunk']
    })

    chunks = GetLinks(table_of_chunks)

    chunks_done = 0
    chunks_todo = len(chunks)
    spinner.text = f'Processing chunks... {chunks_done}/{chunks_todo}'

    # process chunks
    while len(chunks) > 0:
        curr_chunk = chunks.pop()

        soup = GetSoup(args.url + curr_chunk)
        table_in_chunk = soup.find('table', {
            'class': ['allpageslist', 'mw-allpages-table-chunk']
        })

        # parse subordinate chunks
        if 'allpageslist' in table_in_chunk.get('class'):
            new_chunks = GetLinks(table_in_chunk)
            chunks = chunks.union(new_chunks)
            chunks_todo += len(new_chunks)

        # parse pages
        if 'mw-allpages-table-chunk' in table_in_chunk.get('class'):
            for child in table_in_chunk.findChildren():
                for link in child.find_all('a', href=True):
                    article_link = link['href']
                    article = article_link.split('/')[-1]
                    articles.add(article.replace('_', ' '))

        chunks_done += 1
        spinner.text = f'Processing chunks... {chunks_done}/{chunks_todo}'

    spinner.succeed(text='Processing chunks... Done!')

    spinner = Halo(text=f'Printing {len(articles)} articles to file "{args.out.name}"...')
    spinner.start()

    for article in sorted(articles):
        print >> args.out, article

    spinner.succeed(text=f'Printing {len(articles)} articles to file "{args.out.name}"... Done!')


if __name__ == '__main__':
    main()

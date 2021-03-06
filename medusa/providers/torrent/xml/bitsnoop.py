# coding=utf-8
# Author: Gonçalo M. (aka duramato/supergonkas) <supergonkas@gmail.com>
#
# This file is part of Medusa.
#
# Medusa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Medusa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Medusa. If not, see <http://www.gnu.org/licenses/>.
"""Provider code for Bitsnoop."""
from __future__ import unicode_literals

import traceback

from requests.compat import urljoin

from ..torrent_provider import TorrentProvider
from .... import app, logger, tv_cache
from ....bs4_parser import BS4Parser
from ....helper.common import convert_size, try_int


class BitSnoopProvider(TorrentProvider):
    """BitSnoop Torrent provider."""

    def __init__(self):
        """Initialize the class."""
        super(self.__class__, self).__init__('BitSnoop')

        # Credentials
        self.public = True

        # URLs
        self.url = 'https://bitsnoop.com'
        self.urls = {
            'base': self.url,
            'rss': urljoin(self.url, '/new_video.html?fmt=rss'),
            'search': urljoin(self.url, '/search/video/'),
        }

        # Proper Strings
        self.proper_strings = ['PROPER', 'REPACK']

        # Miscellaneous Options

        # Torrent Stats
        self.minseed = None
        self.minleech = None

        # Cache
        self.cache = tv_cache.TVCache(self, search_params={'RSS': ['rss']})

    def search(self, search_strings, age=0, ep_obj=None):
        """
        Search a provider and parse the results.

        :param search_strings: A dict with mode (key) and the search value (value)
        :param age: Not used
        :param ep_obj: Not used
        :returns: A list of search results (structure)
        """
        results = []

        for mode in search_strings:
            logger.log('Search mode: {0}'.format(mode), logger.DEBUG)

            for search_string in search_strings[mode]:
                if mode != 'RSS':
                    logger.log('Search string: {search}'.format
                               (search=search_string), logger.DEBUG)

                search_url = (self.urls['rss'], self.urls['search'] + search_string + '/s/d/1/?fmt=rss')[mode != 'RSS']
                response = self.get_url(search_url, returns='response')
                if not response or not response.text:
                    logger.log('No data returned from provider', logger.DEBUG)
                    continue
                elif not response or not response.text.startswith('<?xml'):
                    logger.log('Expected xml but got something else, is your mirror failing?', logger.INFO)
                    continue

                results += self.parse(response.text, mode)

        return results

    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_rows = html('item')

            for row in torrent_rows:
                try:
                    if not row.category.text.endswith(('TV', 'Anime')):
                        continue

                    title = row.title.text
                    # Use the torcache link bitsnoop provides,
                    # unless it is not torcache or we are not using blackhole
                    # because we want to use magnets if connecting direct to client
                    # so that proxies work.
                    download_url = row.enclosure['url']
                    if app.TORRENT_METHOD != 'blackhole' or 'torcache' not in download_url:
                        download_url = row.find('magneturi').next.replace('CDATA', '').strip('[]') + \
                            self._custom_trackers

                    if not all([title, download_url]):
                        continue

                    seeders = try_int(row.find('numseeders').text)
                    leechers = try_int(row.find('numleechers').text)

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            logger.log("Discarding torrent because it doesn't meet the "
                                       "minimum seeders: {0}. Seeders: {1}".format
                                       (title, seeders), logger.DEBUG)
                        continue

                    torrent_size = row.find('size').text
                    size = convert_size(torrent_size) or -1

                    item = {
                        'title': title,
                        'link': download_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers,
                        'pubdate': None,
                    }
                    if mode != 'RSS':
                        logger.log('Found result: {0} with {1} seeders and {2} leechers'.format
                                   (title, seeders, leechers), logger.DEBUG)

                    items.append(item)
                except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                    logger.log('Failed parsing provider. Traceback: {0!r}'.format
                               (traceback.format_exc()), logger.ERROR)

        return items


provider = BitSnoopProvider()

from click import get_app_dir

from diskcache import Cache

from loguru import logger

from requests import post as http_post

from yarl import URL

from .torrent import Torrent

ENDPOINTDEF = 'https://api.broadcasthe.net/'
EXPIRE = 7 * 24 * 60 * 60


class API(object):
    def __init__(self, api_key, endpoint=ENDPOINTDEF, config_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.endpoint = URL(endpoint) if not isinstance(endpoint, URL) else endpoint
        self.config_path = get_app_dir(__package__) if not config_path else config_path

    # search can be either a search string, or a search array. array currently accepts:
    # - id: Torrent ID
    # - series: Series Name
    # - category: 'Season' or 'Episode'
    # - name: Group Name
    # - search: General text search
    # - codec: one or more of "XViD", "x264", "MPEG2", "DiVX", "DVDR", "VC-1", "h.264", "WMV", "BD", "x264-Hi10P"
    # - container: one or more of "AVI", "MKV", "VOB", "MPEG", "MP4", "ISO", "WMV", "TS", "M4V", "M2TS"
    # - source: one or more of "HDTV","PDTV","DSR","DVDRip","TVRip","VHSRip","Bluray","BDRip","BRRip","DVD5","DVD9","HDDVD","WEB","BD5","BD9","BD25","BD50","Mixed"
    # - resolution: one or more of "Portable Device", "SD", "720p", "1080i", "1080p"
    # - origin: one or more of "Scene", "P2P", "User"
    # - hash: torrent infohash
    # - tvdb: TVDB Series ID
    # - tvrage: tvrage series id
    # - time: time torrent was uploaded.
    # - age: age of the torrent in seconds.
    #
    # Numeric values will accept a prefix of >, <, >=, or <=. eg. {"age": ">=3600"}
    # String fields accept sql LIKE wildcards, but do not use any by default. eg. {"Series": "Simpsons"} will not return results. {"Series": "%Simpsons"} will.
    # % - Represents any number of characters.
    # _ - represents a single character.
    # prefix % or _ with \\ for a literal % or _.
    # All of the field names are case-insensitive, as are the values of the string 'choice' fields.
    def get_torrent(self, hash):
        hash = hash.upper()
        with Cache(self.config_path) as cache:
            if hash not in cache:
                payload = {
                    'method': 'getTorrents',
                    'params': [
                        self.api_key,
                        {
                            'hash': hash
                        },
                        10,
                        0
                    ],
                    'id': 1
                }
                logger.trace(payload)
                r = http_post(self.endpoint,
                              json=payload,
                              headers={
                                  'user-agent': 'illallangi-btnapi/0.0.1'
                              })
                logger.debug('Received {0} bytes from API'.format(len(r.content)))
                logger.trace(r.json())
                if 'result' not in r.json() or 'torrents' not in r.json()['result'] or len(r.json()['result']['torrents']) != 1:
                    logger.error('No response received for hash {hash}')
                    return None
                cache.set(
                    hash,
                    r.json()['result']['torrents'][list(r.json()['result']['torrents'].keys())[0]],
                    expire=EXPIRE)

            return Torrent(cache[hash])

from json import dumps
from time import sleep

from click import get_app_dir

from diskcache import Cache

from loguru import logger

from requests import post as http_post

from yarl import URL

from .index import Index
from .tokenbucket import TokenBucket
from .torrent import Torrent

ENDPOINTDEF = 'https://api.broadcasthe.net/'
SUCCESS_EXPIRYDEF = 7 * 24 * 60 * 60
FAILURE_EXPIRYDEF = 60


class API(object):
    def __init__(
            self,
            api_key,
            endpoint=ENDPOINTDEF,
            cache=True,
            config_path=None,
            success_expiry=SUCCESS_EXPIRYDEF,
            failure_expiry=FAILURE_EXPIRYDEF,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.endpoint = URL(endpoint) if not isinstance(endpoint, URL) else endpoint
        self.cache = cache
        self.config_path = get_app_dir(__package__) if not config_path else config_path
        self.success_expiry = success_expiry
        self.failure_expiry = failure_expiry
        self.bucket = TokenBucket(10, 5 / 10)

    def get_index(self):
        result = self._rpc(self.endpoint, 'userInfo', [self.api_key])
        if result is None:
            return
        return Index(result)

    def rename_torrent_file(self, hash, path):
        return path.lower()

    def get_torrent(self, hash):
        result = self._rpc(self.endpoint, 'getTorrents', [self.api_key, {'hash': hash.upper()}, 1, 0])
        if 'torrents' not in result or len(result['torrents']) != 1:
            logger.error('No response received')
            return None
        return Torrent(result['torrents'][list(result['torrents'].keys())[0]])

    def _rpc(self, url, method, params):
        key = dumps({
            'url': url.human_repr(),
            'method': method,
            'params': params
        })
        with Cache(self.config_path) as cache:
            if not self.cache or key not in cache:
                sleep_time = 5
                while True:
                    self.bucket.consume()
                    payload = {
                        'method': method,
                        'params': params,
                        'id': 1
                    }
                    logger.trace(payload)
                    r = http_post(self.endpoint,
                                  json=payload,
                                  headers={
                                      'User-Agent': 'illallangi-btnapi/0.0.1'
                                  })
                    logger.debug('Received {0} bytes from API'.format(len(r.content)))
                    logger.trace(r.headers)
                    logger.trace(r.json())
                    if r.json().get('error', {}).get('code', 0) == -32002:
                        logger.warning('{}, waiting {} seconds', r.json()['error']['message'], sleep_time)
                        sleep(sleep_time)
                        sleep_time = sleep_time * 2
                        continue
                    if 'result' not in r.json() or r.json()['result'] is None:
                        logger.error('No response received')
                        return None
                    cache.set(
                        key,
                        r.json()['result'],
                        expire=self.success_expiry)
                    break

            return cache[key]

    @property
    def supported_trackers(self):
        return ['landof.tv']

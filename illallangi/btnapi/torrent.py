from functools import cached_property

from bytesize import Size

from loguru import logger

from yarl import URL


class Torrent(object):
    def __init__(self, dictionary, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dictionary = dictionary

        for key in self._dictionary.keys():
            if key not in self._keys:
                logger.error(f'Unhandled key in {self.__class__}: {key}: {type(self._dictionary[key])}"{self._dictionary[key]}"')
                continue
            logger.trace(f'{key}: {type(self._dictionary[key])}"{self._dictionary[key]}"')

    @property
    def _keys(self):
        return [
            'Category',
            'Codec',
            'Container',
            'DownloadURL',
            'GroupID',
            'GroupName',
            'ImdbID',
            'InfoHash',
            'Leechers',
            'Origin',
            'ReleaseName',
            'Resolution',
            'Seeders',
            'Series',
            'SeriesBanner',
            'SeriesID',
            'SeriesPoster',
            'Size',
            'Snatched',
            'Source',
            'Time',
            'TorrentID',
            'TvdbID',
            'TvrageID',
            'YoutubeTrailer',
        ]

    def __repr__(self):
        return f'{self.__class__}{self.infohash} - {self.releasename})'

    def __str__(self):
        return f'{self.infohash} - {self.releasename} ({str(self.size).strip("@")})'

    @cached_property
    def infohash(self):
        return self._dictionary['InfoHash']

    @cached_property
    def releasename(self):
        return self._dictionary['ReleaseName']

    @cached_property
    def downloadurl(self):
        return URL(self._dictionary['DownloadURL']).with_scheme('https')

    @cached_property
    def seriesbanner(self):
        return URL(self._dictionary['SeriesBanner']).with_scheme('https')

    @cached_property
    def seriesposter(self):
        return URL(self._dictionary['SeriesPoster']).with_scheme('https')

    @cached_property
    def youtubetrailer(self):
        return URL(self._dictionary['YoutubeTrailer']).with_scheme('https')

    @cached_property
    def groupid(self):
        return int(self._dictionary['GroupID'])

    @cached_property
    def torrentid(self):
        return int(self._dictionary['TorrentID'])

    @cached_property
    def seriesid(self):
        return int(self._dictionary['SeriesID'])

    @cached_property
    def size(self):
        return Size(int(self._dictionary['Size']))

    @cached_property
    def tvdbid(self):
        return int(self._dictionary['TvdbID'])

    @cached_property
    def tvrageid(self):
        return int(self._dictionary['TvrageID'])

    @cached_property
    def imdbid(self):
        return int(self._dictionary['ImdbID'])

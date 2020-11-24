from functools import cached_property

from bytesize import Size

from loguru import logger


class Index(object):
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
            'UserID',
            'Username',
            'Class',
            'Upload',
            'Download',
            'Bonus',
        ]

    def __repr__(self):
        return f'{self.__class__}{self.username} ({self.userclass})'

    def __str__(self):
        return f'{self.username} ({self.userclass})'

    @cached_property
    def userid(self):
        return int(self._dictionary['UserID'])

    @cached_property
    def username(self):
        return str(self._dictionary['Username'])

    @cached_property
    def userclass(self):
        return str(self._dictionary['Class'])

    @cached_property
    def upload(self):
        return Size(self._dictionary['Upload'])

    @cached_property
    def download(self):
        return Size(self._dictionary['Download'])

    @cached_property
    def bonus(self):
        return float(self._dictionary['Bonus'])

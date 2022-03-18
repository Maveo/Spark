import json
import logging
from string import Formatter


class SafeFormatter(Formatter):
    def get_value(self, key, args, kwargs):
        if isinstance(key, int):
            try:
                return args[key]
            except IndexError:
                return ''
        raise KeyError('Invalid format string key: {}'.format(key))


class FormatString(str):
    formatter = SafeFormatter()

    def format(self, *args: object, **kwargs: object) -> str:
        return self.formatter.format(self, *args, **kwargs)


class I18nManager:
    def __init__(self, path=None, data=None, logger: logging.Logger = None):
        self.logger = logger
        if data is None and path is None:
            raise RuntimeError('i18n initialized without data or file path')
        if data is None:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)

        self.key_not_found = FormatString('i18n-key-not-found')

        self._data = data
        for key in self._data:
            self._data[key] = FormatString(self._data[key])

    def get(self, key: str) -> FormatString:
        if key not in self._data:
            if self.logger is not None:
                self.logger.error(' Key: {} not found in i18n')
            return self.key_not_found
        return self._data[key]

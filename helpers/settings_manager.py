import logging


class GlobalSettingsValidator:
    @staticmethod
    def validate(settings):
        if 'WEBSERVER_SECRET' not in settings:
            settings['WEBSERVER_SECRET'] = None

        if 'SUPER_ADMINS' in settings:
            for s in settings['SUPER_ADMINS']:
                if not isinstance(s, int):
                    raise ValueError('user id must be integer')
        else:
            settings['SUPER_ADMINS'] = None

        if 'LOGGING_LEVEL' not in settings:
            settings['LOGGING_LEVEL'] = logging.WARNING

        if 'WEBSERVER_LOGGING_LEVEL' not in settings:
            settings['WEBSERVER_LOGGING_LEVEL'] = logging.WARNING

        return settings


class Setting:
    def __init__(self, value, description='No description', itype=None, categories=None, preview_call=None):
        self.value = value
        self.description = description
        self.type = itype
        if categories is None:
            categories = []
        self.categories = categories
        self.preview_call = preview_call

    def new_value_dict(self, new_value):
        d = {
            'value': new_value,
            'description': self.description,
            'type': self.type,
            'categories': self.categories
        }
        if self.preview_call is not None:
            d['preview_call'] = self.preview_call
        return d

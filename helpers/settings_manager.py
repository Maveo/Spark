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

class Setting:
    def __init__(self, value, description='No description', itype=None, categories=None):
        self.value = value
        self.description = description
        self.type = itype
        if categories is None:
            categories = []
        self.categories = categories

    def new_value_dict(self, new_value):
        return {
            'value': new_value,
            'description': self.description,
            'type': self.type,
            'categories': self.categories,
        }

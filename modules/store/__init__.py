from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class StoreModule(SparkModule):
    name = 'store'
    title = 'Store'
    description = 'Module allowing to sell and buy'
    dependencies = ['inventory']
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        self.commands = []

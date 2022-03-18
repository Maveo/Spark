from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class ExampleModule(SparkModule):
    name = 'example'
    title = 'Example Module'
    description = 'A module used as an example'
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        self.commands = []

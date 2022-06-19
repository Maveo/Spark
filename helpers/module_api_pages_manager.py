import inspect
from typing import *

import discord

from helpers.exceptions import ModuleNotActivatedException
from webserver import Page

if TYPE_CHECKING:
    from helpers.module_manager import ModuleManager
    from helpers.spark_module import SparkModule


class ModuleApiPagesManager:
    def __init__(self, module_manager: 'ModuleManager'):
        self.module_manager = module_manager
        self.default_api_pages: Dict[str, List[Page]] = {}

    def initialize(self, modules: List['SparkModule']):
        pages_keys: Dict[str, str] = {}
        for module in modules:
            if not isinstance(module.get_api_pages(), list):
                raise RuntimeError('api pages of module {} not list'.format(module.get_name()))
            for api_page in module.get_api_pages():
                if not isinstance(api_page, Page):
                    raise RuntimeError('api page {} of module {} is not of type Page'.format(api_page.path,
                                                                                             module.get_name()))
                if api_page.path in pages_keys:
                    raise RuntimeError('duplicate pages path ({}) in modules {} and {}'.format(
                        api_page.path, module.get_name(), pages_keys[api_page.path]
                    ))
                else:
                    pages_keys[api_page.path] = module.get_name()
                    module_name = module.get_name()
                    wrapped_page = api_page.new(
                        view_func=self.module_wrapper(api_page.view_func, module)
                    )
                    if module_name in self.default_api_pages:
                        self.default_api_pages[module_name].append(wrapped_page)
                    else:
                        self.default_api_pages[module_name] = [wrapped_page]

    def module_wrapper(self, func, module):
        async def _call(guild: discord.Guild, member: discord.Member, *args, **kwargs):
            activated_modules = self.module_manager.get_activated_modules(guild.id)
            if module.get_name() not in activated_modules:
                raise ModuleNotActivatedException(detail='module "{}" not activated'.format(module.get_name()))
            return await func(self.module_manager.get(module.get_name()), guild, member, *args, **kwargs)

        _call.__signature__ = inspect.signature(func)
        return _call

    def items(self) -> ItemsView[str, List[Page]]:
        return self.default_api_pages.items()

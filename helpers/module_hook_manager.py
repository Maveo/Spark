from typing import *


if TYPE_CHECKING:
    from helpers.module_manager import ModuleManager
    from helpers.spark_module import SparkModule


INVENTORY_ITEM_ACTION_HOOK = 'inventory-item-action'


class ModuleHookManager:
    def __init__(self, module_manager: 'ModuleManager'):
        self.module_manager = module_manager
        self.hooks: Dict[str, Dict[str, Dict[str, Dict]]] = {
            INVENTORY_ITEM_ACTION_HOOK: {}
        }

    def add(self, module: 'SparkModule', hook: str, hook_id: str, **kwargs):
        if module.get_name() not in self.hooks[hook]:
            self.hooks[hook][module.get_name()] = {}
        if hook_id in self.hooks[hook][module.get_name()]:
            raise KeyError('Hook Id: {} already exists'.format(hook_id))
        self.hooks[hook][module.get_name()][hook_id] = kwargs

    def get(self, guild_id, key: str) -> Dict[str, Dict]:
        return {hook_id: hook
                for module in self.module_manager.get_activated_modules(guild_id)
                if module in self.hooks[key]
                for hook_id, hook in self.hooks[key][module].items()}

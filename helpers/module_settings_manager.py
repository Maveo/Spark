import itertools
import json
from typing import *

from helpers import tools
from helpers.settings_manager import Setting

if TYPE_CHECKING:
    from helpers.module_manager import ModuleManager
    from helpers.spark_module import SparkModule


class ModuleSettingsManager:
    def __init__(self, module_manager: 'ModuleManager'):
        self.module_manager = module_manager
        self.default_settings: Dict[str, Setting] = {}

    def initialize(self, modules: List['SparkModule']):
        settings_keys: Dict[str, str] = {}
        for module in modules:
            if not isinstance(module.get_settings(), dict):
                raise RuntimeError('settings of module {} not dict'.format(module.get_name()))
            for key, value in module.get_settings().items():
                if not isinstance(value, Setting):
                    raise RuntimeError('setting {} of module {} is not of type Setting'.format(key, module.get_name()))
                if key in settings_keys:
                    raise RuntimeError('duplicate settings key ({}) in modules {} and {}'.format(
                        key, module.get_name(), settings_keys[key]
                    ))
                else:
                    settings_keys[key] = module.get_name()
                    self.default_settings[key] = value

    def keys(self, guild_id=None):
        if guild_id is None:
            return self.default_settings.keys()
        return list(itertools.chain(*map(lambda module: self.module_manager.modules[module].settings.keys(),
                                         self.module_manager.get_activated_modules(guild_id))))

    def all(self, guild_id):
        return {k: self.get(guild_id, k) for k in self.keys(guild_id)}

    def get_default(self, key):
        if key not in self.keys():
            raise KeyError('Key "{}" not found in default settings!'.format(key))
        return self.default_settings[key].value

    def get(self, guild_id, key):
        keys = self.keys(guild_id)
        if key not in keys:
            raise KeyError('Key "{}" not found in guild settings!'.format(key))

        guild_setting = self.module_manager.bot.db.get_setting(guild_id, key)
        if guild_setting is not None:
            try:
                default_type = type(self.default_settings[key].value)
                return tools.simple_eval(default_type, json.loads(guild_setting))
            except Exception as e:
                self.module_manager.bot.logger.warning(e)

        return self.default_settings[key].value

    def preview(self, guild_id, key, value):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))

        value = json.dumps(value)
        default_type = type(self.default_settings[key].value)
        return tools.simple_eval(default_type, json.loads(value))

    def set(self, guild_id, key, value):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))

        try:
            self.preview(guild_id, key, value)
        except Exception as e:
            self.module_manager.bot.logger.warning(e)
            return False
        value = json.dumps(value)
        self.module_manager.bot.db.set_setting(guild_id, key, value)
        return True

    def remove(self, guild_id, key):
        if key not in self.keys(guild_id):
            raise KeyError('Key "{}" not found in default settings!'.format(key))
        self.module_manager.bot.db.remove_setting(guild_id, key)

    def categories(self, guild_id):
        return list(dict.fromkeys(
            [cat for key in self.keys(guild_id) for cat in self.default_settings[key].categories]
        ))

    def all_as_dict(self, guild_id):
        return {
            key: self.default_settings[key].new_value_dict(self.get(guild_id, key)) for key in self.keys(guild_id)
        }


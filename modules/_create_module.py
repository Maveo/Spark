import os
import re


def decapitalize(s):
    if not s:
        return s
    return s[0].lower() + s[1:]


def underscore_to_camelcase(word):
    return ''.join(x.capitalize() for x in word.split('_'))


def underscore_to_spaces(word):
    return ' '.join(x for x in word.split('_'))


def camelcase_to_underscore(word):
    found = re.findall('[A-Z][^A-Z]*', word)
    if len(found) == 0:
        return decapitalize(word)
    return '_'.join(decapitalize(x) for x in found)


INIT_FILE = '''from helpers.spark_module import SparkModule
from .settings import SETTINGS
from .web import API_PAGES


class ${MODULE_NAME_CAMEL}Module(SparkModule):
    name = '${MODULE_NAME_ID}'
    title = '${MODULE_TITLE}'
    description = '$MODULE_DESCRIPTION}'
    dependencies = []
    api_pages = API_PAGES
    settings = SETTINGS

    def __init__(self, bot):
        super().__init__(bot)

        self.commands = []
'''

SETTINGS_FILE = '''from helpers.settings_manager import Setting

SETTINGS = {
    'EXAMPLE_SETTING': Setting(
        value=False,
        description='An example setting',
        itype='bool'
    ),
}
'''

WEB_FILE = '''import discord

from helpers.module_pages import has_permissions
from webserver import Page

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ${MODULE_NAME_CAMEL}Module


@has_permissions(administrator=True)
async def example_func(module: '${MODULE_NAME_CAMEL}Module',
                       guild: discord.Guild,
                       member: discord.Member):
    return {'msg': 'success'}


API_PAGES = [
    Page(path='example', view_func=example_func, methods=['POST']),
]

'''


def create_module(name: str, title: str, description: str, overwrite: bool, current_dir=None):
    if not name:
        raise NameError('Name not provided')
    if current_dir is None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
    if name.lower().endswith('module'):
        name = name[:-6]

    print('Creating module "{}"'.format(name))

    module_id = camelcase_to_underscore(name)
    camel = underscore_to_camelcase(module_id)

    module_path = os.path.join(current_dir, module_id)

    if os.path.isdir(module_path):
        if not overwrite:
            raise FileExistsError('module with name {} already exists'.format(name))
    else:
        os.mkdir(module_path)

    if title == '':
        title = underscore_to_spaces(module_id)

    def replace(s: str):
        return s.replace('${MODULE_NAME_CAMEL}', camel)\
            .replace('${MODULE_NAME_ID}', module_id)\
            .replace('${MODULE_TITLE}', title)\
            .replace('$MODULE_DESCRIPTION}', description)

    with open(os.path.join(module_path, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write(replace(INIT_FILE))

    with open(os.path.join(module_path, 'settings.py'), 'w', encoding='utf-8') as f:
        f.write(replace(SETTINGS_FILE))

    with open(os.path.join(module_path, 'web.py'), 'w', encoding='utf-8') as f:
        f.write(replace(WEB_FILE))

    print('Module "{}" created successful'.format(title))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create a module.')
    parser.add_argument('name', metavar='Name', nargs='?', type=str, help='name of the module')
    parser.add_argument('-t', '--title', type=str,
                        metavar='Title', default='', help='title of the module')
    parser.add_argument('-d', '--description', type=str,
                        metavar='Description', default='Empty Description', help='description of the module')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite existing module')
    args = parser.parse_args()
    if args.name is None:
        args.name = input('Name of the module: ')
    create_module(args.name, args.title, args.description, args.overwrite)

"""Build :py:class:`Recipe` tree from configuration files."""
from ConfigParser import ConfigParser, NoOptionError
import re

from context import Context


DEFAULT_RECIPE = 'novapost.cookbot.recipes:Recipe'


class ConfigParserReader(object):
    """Read configuration from :py:mod:`ConfigParser` files.

    See `ConfigParser documentation`_ for details about the configuration files
    format.

    .. _`ConfigParser documentation`:
       http://docs.python.org/library/configparser.html

    """
    def __init__(self, file_object, context=Context()):
        """Constructor."""
        self.file_object = file_object
        self.parser = None
        self.context = context

    def load_recipe(self, factory_string, name, options):
        """Import recipe factory, return recipe instance.

        Recipe factory is a string representing the path to a Python module
        and an attribute in this module, separated with a ":" character.
        As an example, ``novapost.cookbot.recipes:Recipe`` is the
        default.

        ``name`` and ``options`` arguments will be passed to recipe's factory.

        Recipe factory is generally a class name, i.e. a constructor. But it
        could be any callable, provided it accepts name and options arguments
        and returns a :py:class:`Recipe` instance (or compatible).

        """
        # Import recipe factory.
        (path, factory_name) = factory_string.split(':')
        mod = __import__(path, globals(), locals(), [factory_name], -1)
        factory = getattr(mod, factory_name)
        # Instanciate recipe.
        recipe = factory(self.context, name, options)
        return recipe

    def parse_section(self, name):
        """Parse ``name`` configuration section recursively and return recipe
        instance.

        Each section is supposed to describe a recipe.

        """
        options = dict(self.parser.items(name))
        factory_string = self._get_string(name, 'recipe', DEFAULT_RECIPE)
        recipe = self.load_recipe(factory_string, name, options)
        requirements = self._get_list(name, 'requires')
        recipe.requirements = [self.parse_section(req) for req in requirements]
        parts = self._get_list(name, 'parts')
        recipe.parts = [self.parse_section(part) for part in parts]
        return recipe

    def parse(self, section='main'):
        """Parse self.file_object and return root recipe."""
        self.parser = ConfigParser()
        self.parser.readfp(self.file_object)
        root_recipe = self.parse_section(section)
        return root_recipe

    def _get_list(self, section, option, is_required=False):
        """Utility method to convert an option string to a list of strings."""
        try:
            value = self.parser.get(section, option)
        except NoOptionError, e:
            if is_required:
                raise e
            else:
                value = ''
        if not value:
            return []
        value = re.sub(r'^\s+', '', value)
        value = re.sub(r'\s+$', '', value)
        value = re.split(r'\s+', value)
        return value

    def _get_string(self, section, option, default=None):
        """Utility method to clean option strings."""
        is_required = default is None
        try:
            value = self.parser.get(section, option)
        except NoOptionError, e:
            if is_required:
                raise e
            else:
                value = default
        return value

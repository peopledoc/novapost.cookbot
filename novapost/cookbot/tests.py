"""Unit tests."""
from cStringIO import StringIO
from unittest import TestCase

from wardrobe import StackedDict

from settings import ConfigParserReader
from recipes import Recipe


class TrackerRecipe(Recipe):
    """A recipe that helps tracking install(), enter_context() and
    exit_context() calls."""
    def install(self):
        super(TrackerRecipe, self).enter_context()
        self.context['testing'].append('Install%s' % self.name)

    def update(self):
        super(TrackerRecipe, self).enter_context()
        self.context['testing'].append('Update%s' % self.name)

    def enter_context(self):
        super(TrackerRecipe, self).enter_context()
        self.context['testing'].append('Enter%s' % self.name)

    def exit_context(self):
        super(TrackerRecipe, self).exit_context()
        self.context['testing'].append('Exit%s' % self.name)


class ConfigurationTestCase(TestCase):
    """Test novapost.cookbot.settings.Configuration class."""
    def test_configuration_parser(self):
        """Test loading configuration from a file."""
        configuration_file_contents = """
# Main configuration part.
[main]
parts =
    dev
    staging
    prod

# Environments and machines.

# Dev environment.
[dev]
parts = dev-machine

[dev-machine]
parts =
    www
    media
    db

# Staging environment.
[staging]
parts =
    staging-front
    staging-db

[staging-front]
parts =
    www
    media

[staging-db]
parts = db

# Prod environment.
[prod]
parts =
    prod-www
    prod-media
    prod-db

[prod-www]
parts = www

[prod-media]
parts = media

[prod-db]
parts = db

# Components.

[www]
parts =
    nginx
    django

[media]
parts =
    nginx

[db]
parts = postgresql

# Recipes.

[nginx]
recipe = novapost.cookbot.recipes:Recipe

[django]
recipe = novapost.cookbot.recipes:Recipe

[postgresql]
recipe = novapost.cookbot.recipes:Recipe

"""
        configuration_file = StringIO()
        configuration_file.write(configuration_file_contents)
        configuration_file.seek(0)
        reader = ConfigParserReader(configuration_file)
        reader.parse()


class CmdTestCase(TestCase):
    """Test execution of recipes."""
    def test_execution_order(self):
        """Make sure that walk executes things in order."""
        configuration_file_contents = """
# Main configuration part.
[main]
recipe = novapost.cookbot.tests:TrackerRecipe
requires = Part0
parts =
    Part3
    Part6

[Part0]
recipe = novapost.cookbot.tests:TrackerRecipe

[Part3]
recipe = novapost.cookbot.tests:TrackerRecipe
requires = Part1

[Part1]
recipe = novapost.cookbot.tests:TrackerRecipe
parts = Part2

[Part2]
recipe = novapost.cookbot.tests:TrackerRecipe

[Part6]
recipe = novapost.cookbot.tests:TrackerRecipe
requires =
    Part4
    Part5
parts =
    Part7
    Part8

[Part4]
recipe = novapost.cookbot.tests:TrackerRecipe

[Part5]
recipe = novapost.cookbot.tests:TrackerRecipe

[Part7]
recipe = novapost.cookbot.tests:TrackerRecipe

[Part8]
recipe = novapost.cookbot.tests:TrackerRecipe

"""
        configuration_file = StringIO()
        configuration_file.write(configuration_file_contents)
        configuration_file.seek(0)
        reader = ConfigParserReader(configuration_file)
        recipe = reader.parse()
        # Special 'install' command enters context after execution.
        context = StackedDict()
        context['traversed_recipes'] = []
        context['testing'] = []
        recipe.execute(context, 'install')
        expected_context = ['InstallPart0',
                            'EnterPart0',
                            'Installmain',
                            'Entermain',
                            'InstallPart1',
                            'EnterPart1',
                            'InstallPart2',
                            'EnterPart2',
                            'InstallPart3',
                            'EnterPart3',
                            'ExitPart3',
                            'ExitPart2',
                            'ExitPart1',
                            'InstallPart4',
                            'EnterPart4',
                            'InstallPart5',
                            'EnterPart5',
                            'InstallPart6',
                            'EnterPart6',
                            'InstallPart7',
                            'EnterPart7',
                            'ExitPart7',
                            'InstallPart8',
                            'EnterPart8',
                            'ExitPart8',
                            'ExitPart6',
                            'ExitPart5',
                            'ExitPart4',
                            'Exitmain',
                            'ExitPart0',
                            ]
        self.assertEqual(recipe.context['testing'], expected_context)
        # Non 'install' commands enter context before execution.
        context = StackedDict()
        context['traversed_recipes'] = []
        context['testing'] = []
        recipe.execute(context, 'update')
        expected_context = ['EnterPart0',
                            'UpdatePart0',
                            'Entermain',
                            'Updatemain',
                            'EnterPart1',
                            'UpdatePart1',
                            'EnterPart2',
                            'UpdatePart2',
                            'EnterPart3',
                            'UpdatePart3',
                            'ExitPart3',
                            'ExitPart2',
                            'ExitPart1',
                            'EnterPart4',
                            'UpdatePart4',
                            'EnterPart5',
                            'UpdatePart5',
                            'EnterPart6',
                            'UpdatePart6',
                            'EnterPart7',
                            'UpdatePart7',
                            'ExitPart7',
                            'EnterPart8',
                            'UpdatePart8',
                            'ExitPart8',
                            'ExitPart6',
                            'ExitPart5',
                            'ExitPart4',
                            'Exitmain',
                            'ExitPart0',
                            ]
        self.assertEqual(recipe.context['testing'], expected_context)

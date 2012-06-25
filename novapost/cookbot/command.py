"""Implementation of ``cookbot`` script."""
from optparse import OptionParser

from settings import ConfigParserReader
from context import Context


class Command(object):
    """Command class."""
    def __init__(self):
        """Constructor."""
        self.cmd = None  # The command to invoke.
        self.cmd_args = []  # List of arguments for the command.
        self.cfg = None
        self.environment = None
        self.machine = None
        self.component = None

    def __call__(self):
        """Make it a callable."""
        context = Context()
        return self.recipe.execute(context, self.cmd, self.cmd_args)

    def parse_shell_args(self, *args, **kwargs):
        """Get configuration from :py:meth:`OptionParser.parse_args`."""
        # Defaults.
        configuration_file = 'etc/cookbot.cfg'
        cmd = None
        cmd_args = []
        recipe = None
        # Create and configure parser.
        parser = OptionParser()
        # Parse input.
        (options, arguments) = parser.parse_args(*args, **kwargs)
        # Check options and arguments.
        # Load configuration.
        with open(configuration_file) as configuration_fp:
            recipe = ConfigParserReader(configuration_fp).parse()
        # Check command.
        if not arguments:
            parser.error('Missing command to run.')
        cmd = arguments[0]
        # Command arguments.
        if len(arguments) > 1:
            cmd_args = arguments[1:]
        # Assign local configuration to self.
        self.recipe = recipe
        self.cmd = cmd
        self.cmd_args = cmd_args


def main():
    """Runs command."""
    command = Command()
    command.parse_shell_args()
    command()

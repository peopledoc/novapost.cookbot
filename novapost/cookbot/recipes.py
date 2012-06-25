"""Base recipe classes."""


class Recipe(object):
    """Base class for recipes.

    From a provisioning point of view, recipes are the base unit.
    Compared to Chef's terminology, Recipe can implement ressources, recipes
    or cookbooks.

    A recipe represents a resource. It encapsulates a set of commands that make
    the resource available. As ressources, recipes can be installed,
    configured, updated and uninstalled.

    A recipe has optional requirements. Requirements are a list of recipes that
    have to be available for the current recipe to work. As an example,
    requirements have to be installed first.

    A recipe has optional parts. Parts are a list of recipes that are made
    available through the current recipe. As an example, an environment recipe
    can host several machines. Deploying the whole environment means deploying
    every machine. A machine is deployed in the context of the environment.

    Recipes can expose commands. Commands are things you can call from the
    command line. As an example, a Django recipe would expose a command for
    to run ``manage.py`` commands. "install", "update", "apply" and "uninstall"
    are exposed by default.

    Recipes are organized in trees.

    Recipes can change execution context. See :meth:`enter_context` and
    :meth:`exit_context`.

    """
    def __init__(self, context, name, options):
        """Constructor."""
        self.name = name
        self.context = context
        self.exposed_commands = {}  # Dictionary of exposed commands/callables.
        self.expose('install')
        self.expose('update')
        self.expose('uninstall')
        self.requirements = []  # List of required recipes.
        self.parts = []  # List of child recipes.
        self.parse_options(options)

    def get_default_options(self):
        """Return dictionary with default values for options.

        Override this method rather than the constructor to provide default
        options.

        """
        return {}

    def parse_options(self, options):
        """Parse options, validate them and populate self.options."""
        self.options = self.get_default_options()
        for key, value in options.items():
            self.options[key] = value

    def execute(self, context, cmd, cmd_args=[], enter=True, exit=True):
        """Apply function to recipe's tree in order: requirements, self and
        parts.

        If enter is True, then enter() method is called when a recipe is
        traversed.

        If exit is True, then exit() method is called at the end of the
        traversal.

        """
        self.context = context
        # Traverse requirements. Keep them open. We will exit them at the end.
        for requirement in self.requirements:
            requirement.execute(context, cmd, cmd_args, enter, False)
        # Enter self's context if not special 'install' command.
        if enter and cmd != 'install':
            self.enter()
        # Self execute command.
        if self.is_exposed(cmd):
            func = self.get_callable(cmd)
            if cmd_args:
                func(cmd_args)
            else:
                func()
        # If command was 'install', enter self's context after execution.
        if enter and cmd == 'install':
            self.enter()
        # Traverse parts. Exit them as soon as possible.
        for part in self.parts:
            part.execute(context, cmd, cmd_args, enter, exit)
        # Exit, moonwalking.
        if exit:
            # Parts already exited.
            # Exit self's context.
            self.exit()
            # Exit requirements recursively.
            for requirement in reversed(self.requirements):
                requirement.moonwalk('exit')

    def moonwalk(self, func_name, *args, **kwargs):
        """Apply function to recipe's tree in reverse order: parts, self and
        requirements."""
        for part in reversed(self.parts):
            part.moonwalk(func_name, *args, **kwargs)
        func = getattr(self, func_name)
        func(*args, **kwargs)
        for requirement in reversed(self.requirements):
            requirement.moonwalk(func_name, *args, **kwargs)

    def enter(self):
        """Called when the recipe is traversed forward.

        Default implementation only calls :py:meth:`enter_context`.

        When the tree of recipes is browsed to run a command...

        * if command is "install", :py:meth:`enter_context` is called after the
          command execution. This is a special case because the recipe's
          context cannot be applied if the recipe has not been installed.

        * else we suppose that the recipe has already been installed, so we
          can apply the recipe's context before the command call.

        """
        self.enter_context()

    def exit(self):
        """Called when the recipe is traversed backward.

        Default implementation only calls :py:meth:`exit_context`.

        This method is called after all descendants (i.e. parts) have been
        recursed.

        .. note::

           Remember that a recipe is considered descendant of its requirements.

        """
        self.exit_context()

    def expose(self, command_id, command_callable=None):
        """Register a command to expose: it will be available from the command
        line."""
        self.exposed_commands[command_id] = command_callable

    def is_exposed(self, command_id, recursive=False):
        """Return True if recipe exposes the given command.

        If recursive is True (defaults is False), then the method also returns
        True if at least one requirement or part exposes the command.

        """
        is_exposed = command_id in self.exposed_commands.keys()
        if is_exposed:
            return True
        elif recursive:
            for recipe in self.requirements:
                if recipe.is_exposed(command_id, recursive=True):
                    return True
            for recipe in self.parts:
                if recipe.is_exposed(command_id, recursive=True):
                    return True
        return False

    def get_callable(self, command_id):
        """Return command callable."""
        command_callable = self.exposed_commands[command_id]
        if command_callable is None:
            return getattr(self, command_id)
        else:
            return command_callable

    def enter_context(self, ):
        """Alter context.

        Special method which is called when the recipe is added to the context.
        See :py:meth:`enter`.

        Override this method to modify execution context.

        Example:

        .. code-block:: python

            class UserRecipe(Recipe):
                def enter_context(self):
                    \"\"\"Changes user to use in descendant recipes.\"\"\"
                    self.context.push('user')
                    self.context['user'] = 'you'

                def exit_context(self):
                    \"\"\"Restore context user.\"\"\"
                    self.context.pop('user')

        """

    def exit_context(self):
        """Restore context.

        Special method which is called when the recipe leaves the context.

        """

    def is_installed(self):
        """Return True if the recipe has already been installed."""
        return False

    def install(self):
        """Build and installation process.

        .. note::

           :py:meth:`install` cannot use the recipe's context, unless it
           explicitely calls :py:meth:`enter_context`. Otherwise,
           :py:meth:`enter_context` is called right after :py:meth:`install`
           execution.

        """

    def update(self):
        """Update and upgrade."""

    def uninstall(self):
        """Uninstall recipe."""

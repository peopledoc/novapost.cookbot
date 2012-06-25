"""Manage context variables as dictionary-like stacks."""


class Context(object):
    """Context manager. Handles stacks as a dictionary-like store.
    
    >>> c = Context()
    >>> c.stacks
    {}
    >>> len(c)
    0
    >>> c['a'] = 1
    >>> c['a']
    1
    >>> len(c)
    1
    >>> c['a'] = 2
    >>> c['a']
    2
    >>> c.push('a')
    >>> c['a'] is None
    True
    >>> c['a'] = 'alpha'
    >>> c['a']
    'alpha'
    >>> c.stacks['a']
    ['alpha', 2]
    >>> len(c)
    1
    >>> c.pop('a')
    'alpha'
    >>> c['a']
    2
    >>> c.stacks['a']
    [2]
    >>> len(c)
    1

    """
    def __init__(self):
        """Constructor."""
        self.stacks = {}

    def __len__(self):
        return len(self.stacks)

    def __getitem__(self, key):
        return self.stacks[key][0]

    def __setitem__(self, key, value):
        try:
            self.stacks[key][0] = value
        except KeyError:
            self.stacks[key] = []
            self.stacks[key].append(value)

    def __delitem__(self, key):
        del self.stacks[key]

    def __iter__(self):
        return iter(self.stacks)

    def push(self, key):
        """Push stack at key."""
        try:
            self.stacks[key].insert(0, None)
        except KeyError:
            self.stacks[key] = []
            self.push(key)

    def pop(self, key):
        """Pop key and return value."""
        return self.stacks[key].pop(0)

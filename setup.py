# coding=utf-8
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(name='novapost.cookbot',
      version=read_relative_file('version.txt'),
      description='Contextual execution manager.',
      long_description=open("README.rst").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
                   "Programming Language :: Python",
                   'License :: Other/Proprietary License',
                   ],
      keywords='',
      author='Novapost',
      author_email='rd@novapost.fr',
      url='https://github.com/novagile/novapost.cookbot',
      license='closed source',
      packages=['novapost'],
      namespace_packages=['novapost'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools', 'wardrobe'],
      entry_points={
          "console_scripts": [
              "cookbot = novapost.cookbot.command:main"
          ],
      },
      )

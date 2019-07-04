import codecs
import os
import re

from setuptools import setup, find_packages

PROJECT = 'big_vmatch'


DESCRIPTION = 'bigquant mock trading service'


def find_version(*file_paths):
    def read(*parts):
        with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r') as fp:
            return fp.read()

    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name=PROJECT,
    version=find_version("big_vmatch", "__init__.py"),
    description=DESCRIPTION,

    author='lanms',
    author_email='lanmszhang@gmail.com',

    platforms=['Any'],
    namespace_packages=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
)

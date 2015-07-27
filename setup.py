import sys
from os import path
from codecs import open

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


here = path.abspath(path.dirname(__file__))

setup_requires = ['pytest', 'tox']
install_requires = ['tox', 'aiohttp==0.16.5', 'aioredis==0.2.2']
dev_requires = ['pyflakes', 'pep8', 'pylint', 'check-manifest',
                'ipython', 'ipdb', 'sphinx', 'sphinx_rtd_theme',
                'sphinxcontrib-napoleon']
tests_require = ['pytest-cov', 'pytest-cache', 'pytest-timeout']
dev_requires.append(tests_require)

# Get the long description
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long',
                          '--cov', 'echo', '--cov-report',
                          'term-missing', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='echo',
    version='0.1.0',
    description='An Echo',
    long_description=long_description,
    url='https://github.com/wiliamsouza/echo',
    author='The Echo Authors',
    author_email='wiliamsouza83@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Library',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='mock chaos monkey proxy callback',
    packages=find_packages(exclude=['docs', 'tests*']),
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'dev': dev_requires,
        'test': tests_require,
    },
    cmdclass={'test': PyTest},
)

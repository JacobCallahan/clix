#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'aiofiles',
    'attrs',
    'asyncssh',
    'logzero',
    'pyyaml',
    'pytest',
]

setup(
    name='clix',
    version='0.1.0',
    description="CLI Explorer: Discover, Track, Test.",
    long_description=readme + '\n\n' + history,
    author="Jacob J Callahan",
    author_email='jacob.callahan05@@gmail.com',
    url='https://gitlab.com/jacob.callahan/clix',
    packages=['clix', 'clix.libtools', 'clix.parsers'],
    entry_points={
        'console_scripts': [
            'clix=clix.__main__:Main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='clix',
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ]
)

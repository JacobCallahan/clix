#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()

requirements = ["attrs", "asyncssh", "click","logzero", "pyyaml"]

setup(
    name="clix",
    version="0.2.0",
    description="CLI Explorer: Discover, Track, Test.",
    long_description=readme,
    author="Jacob J Callahan",
    author_email="jacob.callahan05@@gmail.com",
    url="https://gitlab.com/jacob.callahan/clix",
    packages=["clix", "clix.libtools", "clix.parsers"],
    entry_points={"console_scripts": ["clix=clix.commands:cli"]},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords="clix",
    classifiers=[
        "Development Status :: 2 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
)

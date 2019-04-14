#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name="HelloWorld",
    version="0.1",
    packages=find_packages(),
    install_requires=['hydrus @ https://gitlab.com/cryzed/hydrus-api/-/archive/master/hydrus-api-master.zip']
)

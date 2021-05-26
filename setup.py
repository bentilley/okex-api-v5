# setup.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from setuptools import setup, find_packages


setup(
    name="okex-api-v5",
    version="0.1.0",
    packages=find_packages(include=["client", "client.*"]),
)

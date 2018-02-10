# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

with open('echoscraper/__init__.py') as fd:
    version = re.search(
        r'^__version__\s*=\s*"(.*)"',
        fd.read(),
        re.M
    ).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

# args==0.1.0
# astroid==1.6.0
# certifi==2018.1.18
# chardet==3.0.4
# idna==2.6
# isort==4.2.15
# lazy-object-proxy==1.3.1
# mccabe==0.6.1
# pylint==1.8.1
# six==1.11.0
# urllib3==1.22
# wrapt==1.10.11

requirements = ["clint==0.5.1", "lxml==4.1.1", "requests==2.18.4"]

setup(
    name = "echoscraper",
    packages = ["echoscraper"],
    entry_points = {
        "console_scripts": ['echoscraper = echoscraper.echoscraper:main']
        },
    version = version,
    description = "Automatically downloads lectures from Echo360.org.",
    long_description = long_descr,
    author = "ChickaChickaChicka",
    author_email = "gatecrasher53@gmail.com",
    # url = "http://gehrcke.de/2014/02/distributing-a-python-command-line-application",
    install_requires = requirements
)
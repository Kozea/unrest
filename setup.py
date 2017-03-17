#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of unrest
#
# A troubling rest api library for sqlalchemy models
# Copyright © 2017 Kozea Florian Mounier
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.

from setuptools import find_packages, setup

__version__ = '0.1.7'


tests_requirements = [
    'pytest-runner', 'pytest-cov', 'pytest-flake8', 'pytest-isort',
    'pytest', 'flask', 'flask-sqlalchemy'
]

setup(
    name="unrest",
    version=__version__,
    description="A troubling rest api library for sqlalchemy models "
    "(pre-release)",
    author="Kozea",
    author_email="florian.mounier@kozea.fr",
    license="GNU LGPL v3+",
    platforms="Any",
    packages=find_packages(),
    provides=['unrest'],
    keywords=['rest', 'flask', 'api', 'sqlalchemy'],
    install_requires=['sqlalchemy', 'python-dateutil'],
    setup_requires=['pytest-runner'],
    test_requires=tests_requirements,
    extras_require={
        'test': tests_requirements
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"])

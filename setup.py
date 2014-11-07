#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='urlquery',
    version='2.0.1',
    description='Python API to access urlquery v2',
    url='https://github.com/CIRCL/urlquery-py',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['urlquery'],
    license='GNU GPLv3',
    install_requires=['requests', 'python-dateutil'],
)

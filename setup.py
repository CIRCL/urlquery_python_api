#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='urlquery',
    version='2.1',
    description='Python API to access urlquery v2',
    url='https://github.com/CIRCL/urlquery-py',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['urlquery'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ],
    install_requires=['requests', 'python-dateutil'],
)

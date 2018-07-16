#!/usr/bin/env python
# coding: utf-8
'''
The setup script for pykit-bsc
'''
import setuptools
from pykit import __version__

with open('README.md', 'r') as fh:
    long_desc = fh.read()

with open('requirements.txt', 'r') as fh:
    for line in fh.readlines():
        if line.strip() and not line.strip().startswith('#'):
            inst_requ = [line.strip('\n')]

setuptools.setup(
    name='pykit-bsc-s2',
    version=__version__,
    description='A collection of toolkit lib for distributed system development in python',
    long_description=long_desc,
    url='https://github.com/bsc-s2/pykit',
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    license='MIT',
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=inst_requ,
    python_requires='>=2.7,!=3.0.*,!=3.1.*',
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)

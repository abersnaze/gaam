# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='gaam',
    version='0.1.0',
    description='Vid Game',
    long_description=readme,
    author='George Campbell',
    author_email='abersnaze@gmail.com',
    license=license,
    packages=find_packages(exclude=('tests'))
)


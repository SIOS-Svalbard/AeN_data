#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

with open('requirements.txt') as fid:
    REQUIRES = [l.strip() for l in fid.readlines() if l]
setup(name='AeN_data',
      version='1.0',
      description='Scripts and sql queries for inserting and modifying the Nansen
      Legacy sample databaset',
      author='Pål Ellingsen',
      author_email='pale@unis.com',
      packages=[],
      install_requires=REQUIRES,
      url='https://github.com/SIOS-Svalbard/Aen_data',
      long_description=open('README.txt').read(),
      scripts=[],)


# if __name__ == "__main__":

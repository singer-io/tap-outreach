#!/usr/bin/env python

from setuptools import setup

setup(name='tap-outreach',
      version='0.1.0',
      description='Singer.io tap for extracting data from the Outreach.io API',
      author='Stitch',
      url='https://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_outreach'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.22.0',
          'singer-python==5.8.0'
      ],
      entry_points='''
          [console_scripts]
          tap-outreach=tap_outreach:main
      ''',
      packages=['tap_outreach'],
      package_data = {
          'tap_outreach': ['schemas/*.json'],
      }
)

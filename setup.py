#!/usr/bin/env python

from setuptools import setup

setup(name='tap-outreach',
      version='1.1.3',
      description='Singer.io tap for extracting data from the Outreach.io API',
      author='Stitch',
      url='https://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_outreach'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.31.0',
          'singer-python==5.9.0'
      ],
      extras_require={
          'dev': [
              'ipdb',
              'nose',
              'pylint==2.6.2',
              'requests-mock==1.9.3'
          ]
      },
      entry_points='''
          [console_scripts]
          tap-outreach=tap_outreach:main
      ''',
      packages=['tap_outreach'],
      package_data = {
          'tap_outreach': ['schemas/*.json'],
      }
)

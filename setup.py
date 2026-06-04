#!/usr/bin/env python

from setuptools import setup

setup(name='tap-outreach',
      version='1.2.2',
      description='Singer.io tap for extracting data from the Outreach.io API',
      author='Stitch',
      url='https://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_outreach'],
      install_requires=[
          'backoff==2.2.1',
          'requests==2.33.0',
          'singer-python==6.1.1'
      ],
      extras_require={
          'dev': [
              'ipdb',
              'nose',
              'pylint',
              'requests-mock'
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

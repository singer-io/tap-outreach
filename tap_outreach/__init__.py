#!/usr/bin/env python3

import sys
import json
import argparse

import singer
from singer import metadata

from tap_outreach.client import OutreachClient
from tap_outreach.discover import discover
from tap_outreach.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    'start_date',
    'client_id',
    'client_secret',
    'redirect_uri',
    'refresh_token'
]

def do_discover(client):
    LOGGER.info('Testing authentication')
    try:
        client.get(
            'stages',
            endpoint='stages')
    except:
        raise Exception('Error testing Outreach authentication')

    LOGGER.info('Starting discover')
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info('Finished discover')

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    with OutreachClient(parsed_args.config) as client:
        if parsed_args.discover:
            do_discover(client)
        else:
            sync(client,
                 parsed_args.catalog,
                 parsed_args.state,
                 parsed_args.config['start_date'])

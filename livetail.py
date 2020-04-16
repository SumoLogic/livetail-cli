#!/usr/bin/env python

# -----------------------------------------------------------
# Live Tail CLI
#
# This script allows you to start and use a Live Tail session from the command line.
#
# You need to provide you Access Id and Access Key when prompted and the script will be able to automatically determine
# the deployment where your account exists.
#
# If you would like to use the Live Tail CLI with a Sumo internal staging deployment
# please specify the deployment in the program arguments using the -d option
# as it cannot be determined automatically.
# -----------------------------------------------------------

import argparse
import getpass
import json
import logging
import requests
import sys
import time
import os

# Version 2.0
MAJOR_VERSION = 2
MINOR_VERSION = 0
CONFIG_FILE = 'config.json'
HEADERS = {'Content-Type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/46.0.2490.80 Safari/537.36',
           'Accept': 'application/json'}
LIVE_TAIL_VERSION_ENDPOINT = 'livetail/session/version'
DEFAULT_SUMOLOGIC_DEPLOYMENT = 'api.sumologic.com'

LOGGER = logging.getLogger('Live Tail CLI')
LOGGER.setLevel(logging.INFO)
logger_handler = logging.StreamHandler()
logger_handler.setLevel(logging.INFO)
LOGGER.addHandler(logger_handler)


def get_sumo_logic_api_url(deployment, endpoint):
    return f'https://{deployment}/api/v1/{endpoint}'


def resolve_deployment(session, access_id, access_key):
    """
    Automatically determines a deployment that a user has access to.

    If a specific deployment has not been provided as part of the program args
    it is resolved using a redirect method:

    a request is made to a default production API endpoint,
    based on a given Access Id, a user gets redirected to a deployment where their account exists
    and the deployment URL is retrieved from the response url.
    """

    deployment = DEFAULT_SUMOLOGIC_DEPLOYMENT
    url = get_sumo_logic_api_url(deployment, LIVE_TAIL_VERSION_ENDPOINT)

    try:
        response = session.get(url, headers=HEADERS, auth=(access_id, access_key))
        deployment = response.url.split('/api/v1/')[0].split('https://')[1]
    except Exception as e:
        LOGGER.error('### Unable to resolve deployment using the Access Id / Access Key ###', exc_info=e)
        sys.exit()

    return deployment


def authenticate(session, access_id, access_key, deployment):
    """
    Checks if a user is authorized to access the API on a given deployment.

    Authentication is considered successful if a user is able to successfully call into an API endpoint
    for a given deployment.
    """

    LOGGER.info('### Authenticating ###')
    version_url = get_sumo_logic_api_url(deployment, LIVE_TAIL_VERSION_ENDPOINT)
    response = session.get(version_url, headers=HEADERS, auth=(access_id, access_key))

    if response.status_code != requests.codes.ok:
        LOGGER.error('### Authentication failed. Please check the Access ID and Access Key and try again ###')
        sys.exit()

    LOGGER.info('### Authentication successful ###')

    check_for_version(response)


def check_for_version(version_info):
    latest_version = str(version_info.json()['version'])
    latest_major_version = float(latest_version.split('.')[0])
    latest_minor_version = float(latest_version.split('.')[1])

    if latest_major_version > MAJOR_VERSION:
        LOGGER.error('### Incompatible version of CLI. Please download the latest version from \n'
                     'https://github.com/sumologic/livetail-cli ###')
        sys.exit()

    if latest_minor_version > MINOR_VERSION:
        LOGGER.warning('### A newer version of Live Tail CLI is available, '
                       'but your current version will still function. \n'
                       'If you would like to download the latest version, '
                       'go to https://github.com/sumologic/livetail-cli  ###')


def create_live_tail_session(session, access_id, access_key, deployment, live_tail_filter):
    live_tail_session_url = get_sumo_logic_api_url(deployment, 'livetail/session')
    live_tail_session_response = session.post(live_tail_session_url,
                                              json={'filter': live_tail_filter, 'isCLI': True},
                                              headers=HEADERS,
                                              auth=(access_id, access_key))

    if live_tail_session_response.status_code != requests.codes.ok:
        LOGGER.error('### Unable to create Live Tail session. Please try again ###')
        sys.exit()

    if live_tail_session_response.json()['error']:
        LOGGER.error('### Failed to create Live Tail session because ' +
                     live_tail_session_response.json()['errorMessage'] + ' ###')
        sys.exit()

    tail_id = live_tail_session_response.json()["id"]

    return tail_id


def start_live_tail_session(session, access_id, access_key, deployment, live_tail_filter):
    tail_id = None
    try:
        tail_id = create_live_tail_session(session, access_id, access_key, deployment, live_tail_filter)
        time.sleep(2)  # Give some time for the engine to be ready

        LOGGER.info('### Starting Live Tail session ###')
        offset = 0

        while True:
            latest_live_tail_results_url = get_sumo_logic_api_url(deployment,
                                                                  f'livetail/session/{tail_id}/latest/{offset}')
            response = session.get(latest_live_tail_results_url,
                                   headers=HEADERS,
                                   auth=(access_id, access_key))

            try:
                state = response.json()['state']
            except ValueError:
                LOGGER.error('### API rate limit exceeded. Ending this Live Tail session ###')
                sys.exit()

            if state is not None:
                offset = state['currentOffset'] + 1
                messages = response.json()['messages']
                user_messages = state['userMessages']
                is_stopped = state['isStopped']

                for usr_msg in user_messages:
                    message_type = usr_msg['messageType']
                    if 'currentRate' in usr_msg:
                        if message_type == 'Error':
                            LOGGER.error('### Your query produced too many messages and caused the session to end. '
                                         'Please add additional metadata fields to your query to make it '
                                         'more specific. ###')
                            sys.exit()
                        elif message_type == 'Warning':
                            LOGGER.warning('### Your query is producing too many messages and will cause the session '
                                           'to end. Please add additional metadata fields to your query to make it '
                                           'more specific. ###')

                    if 'maxEngineRunningTime' in usr_msg:
                        if message_type == 'Error':
                            LOGGER.error('### Your Live Tail session has timed out. ###')
                            sys.exit()

                if is_stopped:
                    LOGGER.error('### Your Live Tail session has timed out. ###')
                    sys.exit()

                for msg in messages:
                    print(msg['payload'])

            time.sleep(1)

    except Exception as e:
        LOGGER.error("### Fatal error has occurred. The Live Tail session will end. ###", exc_info=e)

    finally:
        if tail_id is not None:
            LOGGER.info('### Ending the Live Tail session ###')
            delete_url = get_sumo_logic_api_url(deployment, f'livetail/session/{tail_id}')
            session.delete(delete_url, headers=HEADERS, auth=(access_id, access_key))
        sys.exit()


def parse_program_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('filter', type=str, help='Live Tail filter', default=None, nargs='?')
    parser.add_argument('-i', dest='accessId', type=str, help='Access ID', required=False)
    parser.add_argument('-k', dest='accessKey', type=str, help='Access Key', required=False)
    parser.add_argument('-d', dest='deployment', type=str,
                        help='Deployment-specific Sumo Logic API URL e.g. api.sumologic.com', required=False)

    parser.add_argument('-v', '--version', action='version',
                        version=f'Sumo Logic Live Tail CLI Version ({MAJOR_VERSION}.{MINOR_VERSION})')

    parser.add_argument('-c', dest='clear', action='store_true', help='clear Live Tail')

    args = parser.parse_args()

    if args.accessId is None and args.accessKey is not None:
        LOGGER.error('### Please provide the Access ID with the -i argument ###')
        sys.exit()

    if args.accessId is not None and args.accessKey is None:
        LOGGER.error('### Please provide the Access Key with the -k argument ###')
        sys.exit()

    # delete config file on clear
    if args.clear:
        LOGGER.info('### Clearing Live Tail CLI session ###')
        try:
            os.remove(CONFIG_FILE)
        except OSError:
            pass
        sys.exit()

    return args


def get_access_details(program_args):
    if not os.path.exists(CONFIG_FILE):
        config_data = {'deployment': '', 'accessId': '', 'accessKey': ''}
    else:
        with open(CONFIG_FILE) as json_data:
            config_data = json.load(json_data)

    if program_args.accessId is None and program_args.accessKey is None:  # Args not specified - read from file
        access_id = config_data['accessId']
        access_key = config_data['accessKey']
    else:
        access_id = program_args.accessId
        access_key = program_args.accessKey

    has_asked_for_access_id = False
    if access_id is None or access_id == "":
        access_id = input('Please enter your Access ID: ')
        access_key = getpass.getpass('Please enter your Access Key')  # Asks for password without echoing
        has_asked_for_access_id = True

    return access_id, access_key, has_asked_for_access_id


def launch_live_tail():
    LOGGER.info('### Welcome to Sumo Logic Live Tail Command Line Interface ###')

    args = parse_program_args()
    access_id, access_key, has_asked_for_access_id = get_access_details(args)
    session = requests.Session()

    # a deployment is determined automatically if it has not been provided in the command line
    if args.deployment is None or args.deployment == '':
        deployment = resolve_deployment(session, access_id, access_key)
    else:
        deployment = args.deployment

    # verify whether a user has access to a given deployment
    authenticate(session, access_id, access_key, deployment)

    # if a user has been explicitly asked for login details, they are saved in the CONFIG_FILE
    if has_asked_for_access_id:
        with open(CONFIG_FILE, 'w') as outfile:
            json.dump({'deployment': deployment, 'accessId': access_id, 'accessKey': access_key}, outfile)

    start_live_tail_session(session, access_id, access_key, deployment, args.filter)


if __name__ == '__main__':
    launch_live_tail()
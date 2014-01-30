#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2014 Dave Kludt
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import sys
import argparse
import requests
import json
import re


__version__ = '0.1'


def process_api_request(url, verb, data, headers):
    if data:
        response = getattr(requests, verb.lower())(
            url,
            headers=headers,
            data=json.dumps(data)
        )
    else:
        response = getattr(requests, verb.lower())(url, headers=headers)

    response_headers = dict(response.headers)

    try:
        content = json.loads(response.content)
    except:
        temp = re.findall('<body>(.+?)<\/body>', response.content, re.S)
        if temp:
            formatted_content = re.sub(
                '\n|\r|\s\s+?|<br \/>|<h1>',
                '',
                temp[0]
            )
            content = re.sub('<\/h1>', '<br />', formatted_content)
        else:
            content = "No content recieved. Status Code: %s" % str(
                response.status_code
            )

    return content, response.status_code


def generate_autoscale_header(token):
    header = {
        'Content-Type': 'application/json',
        'X-Auth-Token': token
    }
    return header


def generate_autoscale_url(data_center, account_number, uri):
    return 'https://%s.autoscale.api.rackspacecloud.com/v1.0/%s%s' % (
        data_center.lower(),
        account_number,
        uri
    )


def generate_webhook_data(args):
    data = [
        {
            "name": args.webhook_name
        }
    ]
    return data


def generate_autoscale_data(args):
    group_config = {
        'cooldown': args.group_cooldown,
        'minEntities': args.min_entities,
        'maxEntities': args.max_entities,
        'name': args.group_name
    }
    launch_config = {
        'args': {
            'server': {
                'flavorRef': args.flavor_id,
                'imageRef': args.image_id,
            }
        },
        'type': 'launch_server'
    }
    if args.server_name:
        launch_config['args']['server']['name'] = args.server_name

    meta_data = {}
    if args.meta_pair:
        for pair in args.meta_pair:
            if re.search('=', pair):
                temp_key, temp_value = pair.split('=')
                meta_data[temp_key] = temp_value
            else:
                print (
                    '\n********************* WARNING *************************'
                    '\nMetadata not added as it was not formatted correctly.'
                    '\nUse Meta-Key=Meta-Value format in the request'
                    '\nMeta key pair used: %s'
                    '\n*******************************************************'
                ) % pair
        launch_config['args']['server']['metadata'] = meta_data

    all_networks = []
    if not args.no_public:
        all_networks.append(
            {'uuid': '00000000-0000-0000-0000-000000000000'}
        )

    if not args.no_service:
        all_networks.append(
            {'uuid': '11111111-1111-1111-1111-111111111111'}
        )

    if args.networks:
        for network in args.networks:
            all_networks.append({'uuid': network})

    launch_config['args']['server']['networks'] = all_networks

    policy_config = [
        {
            'cooldown': args.policy_cooldown,
            'change': args.policy_change,
            'name': args.policy_name,
            'type': 'webhook'
        }
    ]
    if args.policy_change:
        if args.policy_change > 0:
            temp_change = (args.policy_change * 2)
            temp_change = args.policy_change - temp_change
            temp_name = '%s Remove' % args.policy_name
            policy_config.append(
                {
                    'cooldown': args.policy_cooldown,
                    'change': temp_change,
                    'name': temp_name,
                    'type': 'webhook'
                }
            )

    data = {
        'groupConfiguration': group_config,
        'launchConfiguration': launch_config,
        'scalingPolicies': policy_config
    }
    return data


def cloud_authentication(username, api_key):
    account_number, token = None, None
    auth_url = 'https://identity.api.rackspacecloud.com/v2.0/tokens'
    auth_header = {
        'Content-Type': 'application/json',
    }
    data = {
        "auth": {
            "RAX-KSKEY:apiKeyCredentials": {
                "apiKey": api_key,
                "username": username
            }
        }
    }
    content, status_code = process_api_request(
        auth_url,
        'POST',
        data,
        auth_header
    )
    if status_code >= 400:
        exit(
            '\nCould not authenticate with the credentials provided. '
            'Please check the values and try again'
        )

    token = content.get('access').get('token').get('id')
    account_number = content.get('access').get('token').get('tenant').get('id')
    return account_number, token


def options():
    parser = argparse.ArgumentParser(
        description=('AutoScale group, policy, webhook, and launch '
                     'configuration setup program')
    )
    parser.add_argument('-u',
                        '--username',
                        dest='username',
                        help='Cloud account user name',
                        metavar='<username>',
                        required=True)
    parser.add_argument('-k',
                        '--api-key',
                        dest='api_key',
                        help='Cloud users API key',
                        metavar='<api-key>',
                        required=True)
    parser.add_argument('-r',
                        '--region',
                        dest='data_center',
                        metavar='<data-center>',
                        required=True,
                        help='Data center region to create the autoscale '
                             'group in')
    parser.add_argument('-n',
                        '--name',
                        dest='group_name',
                        help='Name for the auto scale group being created',
                        metavar='<group_name>',
                        required=True)
    parser.add_argument('--flavor',
                        dest='flavor_id',
                        metavar='<flavor_id>',
                        required=True,
                        help='Flavor ID for to be used for all servers '
                             'created under this auto scale group')
    parser.add_argument('--image',
                        dest='image_id',
                        metavar='<image_uuid>',
                        required=True,
                        help='Image UUID used to create every server under '
                             'this auto scale group')
    parser.add_argument('--server-name',
                        dest='server_name',
                        metavar='<server_name>',
                        help='Server name to prepend to the auto generated '
                             'server name when a server is created')
    parser.add_argument('--meta',
                        dest='meta_pair',
                        metavar='<key=value>',
                        nargs='*',
                        help='Meta key/value pair to set on each '
                             'created server')
    parser.add_argument('--no-public',
                        dest='no_public',
                        action='store_true',
                        help='Do not connect new servers to Public Net')
    parser.add_argument('--no-service',
                        dest='no_service',
                        action='store_true',
                        help='Do not connect new servers to Service Net')
    parser.add_argument('--networks',
                        dest='networks',
                        metavar='<network-uuid>',
                        nargs='*',
                        help='Connect to additional networks by listing '
                             'the network UUIDs')
    parser.add_argument('--group-cooldown',
                        type=int,
                        dest='group_cooldown',
                        default=60,
                        metavar='<group-cooldown>',
                        help='Group cooldown in seconds to wait for '
                             'the next action : Default is 60 seconds')
    parser.add_argument('--group-min',
                        type=int,
                        dest='min_entities',
                        default=0,
                        metavar='<min-servers>',
                        help='Minimum number of servers that can be '
                             'in the group : Default is 0')
    parser.add_argument('--group-max',
                        type=int,
                        dest='max_entities',
                        default=10,
                        metavar='<max-servers>',
                        help='Maximum number of servers that can be '
                             'created for the current group'
                             ' : Default is 10')
    parser.add_argument('--policy-cooldown',
                        type=int,
                        dest='policy_cooldown',
                        default=60,
                        metavar='<policy-cooldown>',
                        help='Number of seconds for cooldown on policy'
                             ' : Default is 60 seconds')
    parser.add_argument('--policy-change',
                        type=int,
                        dest='policy_change',
                        default=1,
                        metavar='<policy-change>',
                        help='Number of servers to change either positive or '
                             'negative when the policy is executed  '
                             ' : Default is 1')
    parser.add_argument('--policy-name',
                        dest='policy_name',
                        metavar='<policy-name>',
                        default='Default Policy',
                        help='Name of the default policy to be created'
                             ' : Defaults to "Default Policy"')
    parser.add_argument('--webhook-name',
                        dest='webhook_name',
                        metavar='<webhook-name>',
                        default='Default Webhook',
                        help='Name of the default webhookto use'
                             ' : Defaults to "Default Webhook"')
    parser.add_argument('--dry-run',
                        dest='dry_run',
                        action='store_true',
                        default=False,
                        help='Display URLs and data objects for '
                             'group and webhooks')
    parser.add_argument('-v',
                        '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='Show all information')

    args = parser.parse_args()
    return args


def shell():
    args = options()
    policy_ids, policy_names, webhook_anon_urls = [], [], []
    if args.dry_run:
        print '\nStarting dry run for Auto Scale group setup'
    else:
        print '\nStarting execution for Auto Scale group setup'

    account_number, token = cloud_authentication(args.username, args.api_key)
    data_object = generate_autoscale_data(args)
    autoscale_url = generate_autoscale_url(
        args.data_center,
        account_number,
        '/groups'
    )
    header = generate_autoscale_header(token)

    if args.dry_run:
        print '\nGroup endpoint to send POST request to:'
        print autoscale_url
        print '\nGroup Configuration Object to be sent through API'
        print json.dumps(data_object, sort_keys=False, indent=4)
    else:
        content, status_code = process_api_request(
            autoscale_url,
            'POST',
            data_object,
            header
        )
        if status_code >= 400:
            exit('\n%s' % content)

        print '\nGroup successfully created'
        if args.verbose:
            print json.dumps(content, sort_keys=False, indent=4)

    if args.dry_run:
        group_id = '<GROUP-ID>'
        policy_ids = ['<POLICY-ID>']
    else:
        group_id = content.get('group').get('id')
        for policy in content.get('group').get('scalingPolicies'):
            policy_ids.append(policy.get('id'))
            policy_names.append(policy.get('name'))

    for policy_id in policy_ids:
        webhook_url = generate_autoscale_url(
            args.data_center,
            account_number,
            '/groups/%s/policies/%s/webhooks' % (
                group_id,
                policy_id
            )
        )
        webhook_data = generate_webhook_data(args)

        if args.dry_run:
            print '\nWebhook endpoint to send POST request to:'
            print webhook_url
            print '\nWebhook data object to be sent through API'
            print json.dumps(webhook_data, sort_keys=False, indent=4)
            exit()
        else:
            content, status_code = process_api_request(
                webhook_url,
                'POST',
                webhook_data,
                header
            )

        if status_code >= 400:
            exit('\n%s' % content)

        print '\nWebhook was successfully created'
        if args.verbose:
            print json.dumps(content, sort_keys=False, indent=4)

        webhook_links = content.get('webhooks')[0].get('links')
        for link in webhook_links:
            if link.get('rel') == 'capability':
                webhook_anon_urls.append(link.get('href'))

    if args.verbose:
        doc_url = (
            'http://docs.rackspace.com/cas/api/v1.0/autoscale-devguide/content'
            '/POST_anonymousExecute_v1.0_execute__capability_version___'
            'capability_hash__Executions.html'
        )
        print (
            '\nTo use the webhook(s) you will need to issue a POST request to '
            'the following URL(s):'
        )
        for i in range(len(webhook_anon_urls)):
            print '\nWebhook URL for Policy - %s:\n%s' % (
                policy_names[i],
                webhook_anon_urls[i]
            )
        print (
            '\nFor example for the two new webhooks you could issue the request '
            'like the following:\n'
        )
        for i in range(len(webhook_anon_urls)):
            print (
                'Curl request for Policy - %s:\ncurl -XPOST -H "Content-'
                'Type: application/json" %s\n' % (
                    policy_names[i],
                    webhook_anon_urls[i]
                )
            )
        print (
            'You should recieve a status return code of 202 once complete.'
            '\n\nYou can view the doumentation at the following URL for more'
            ' information:\n%s\n'
        ) % doc_url
    else:
        print '\n------------------ WebHook URLs --------------------'
        for i in range(len(webhook_anon_urls)):
            print '\nWebhook URL for Policy - %s:\n%s' % (
                policy_names[i],
                webhook_anon_urls[i]
            )
        print '\n----------------------------------------------------\n'


if __name__ == '__main__':
    try:
        shell()
    except:
        e = sys.exc_info()[1]
        if isinstance(e, SystemExit):
            raise
        else:
            raise SystemExit(e)

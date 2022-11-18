#!/usr/bin/env python
"""
Read existing queues and dump information to stdout and into a CSV file

usage: read_queues.py [-h] [--one_column]

optional arguments:
  -h, --help            show this help message and exit
  --one_column, -1, -o  Create a single column with agent names

optional arguments:
  -h, --help       show this help message and exit

"""
import asyncio
import csv
import logging
import os
import sys
from argparse import ArgumentParser
from itertools import chain

from dotenv import load_dotenv
from wxc_sdk.as_api import AsWebexSimpleApi
from wxc_sdk.telephony.callqueue import CallQueue
from wxc_sdk.telephony.hg_and_cq import Agent

from integration_token import get_tokens


def agent_name(agent: Agent) -> str:
    """
    Helper: name of an agent
    """
    return f'{agent.first_name} {agent.last_name}'


async def main():
    # enable DEBUG logging to a file; REST log shows all requests
    logging.basicConfig(filename=os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.log'),
                        filemode='w', level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument('--one_column', '-1', '-o', help='Create a single column with agent names',
                        action='store_true', required=False, dest='single_agent_column')
    args = parser.parse_args()

    # get environment variables from .env; required for integration parameters
    load_dotenv()

    # get tokens from cache or create a new set of tokens using the integration defined in .env
    tokens = get_tokens()
    async with AsWebexSimpleApi(tokens=tokens) as api:

        # list all existing queues
        queues = await api.telephony.callqueue.list()
        print(f'Got {len(queues)} queues')

        # get details for all call queues. list() response doesn't have the agents
        details = await asyncio.gather(*[api.telephony.callqueue.details(location_id=queue.location_id,
                                                                         queue_id=queue.id)
                                         for queue in queues])
        print(f'Got details for {len(details)} queues')
        details: list[CallQueue]

        # print a summary
        for queue, detail in zip(queues, details):
            print(f'queue "{queue.name}"')
            print(f'  location: "{queue.location_name}"')
            print(f'  phone number: {detail.phone_number}')
            print(f'  extension: {detail.extension}')
            print(f'  agents: '
                  f'{", ".join(map(agent_name, detail.agents))}')

        # create a CSV with queue summaries

        # agent names: set of agent names of all agents in all queues
        all_agent_names = sorted(set(chain.from_iterable(map(agent_name, detail.agents)
                                                         for detail in details)))
        # column headers
        field_names = ['name', 'location', 'phone number', 'extension']
        if args.single_agent_column:
            # single "agents" column for comma separated lists of agent names
            field_names.append('agents')
        else:
            # ... or one column for each agent
            field_names.extend(all_agent_names)

        # open a CSV file based on the name of this source
        with open(os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.csv'),
                  mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            # write one row for each queue
            for queue, detail in zip(queues, details):
                # base attributes
                row = {'name': queue.name,
                       'location': queue.location_name,
                       'phone number': detail.phone_number,
                       'extension': detail.extension}

                # generator for agent names in this queue
                agents_in_queue = map(agent_name, detail.agents)
                if args.single_agent_column:
                    # comma separated list pf agent names
                    row['agents'] = ','.join(agents_in_queue)
                else:
                    # for each agent column we want to put the index of the agent in the list of agents in this queue
                    # ... or an empty string
                    agent_idx = {name: i for i, name in enumerate(agents_in_queue)}
                    for name in all_agent_names:
                        row[name] = agent_idx.get(name, '')
                writer.writerow(row)
            # for
        # with
        return


if __name__ == '__main__':
    asyncio.run(main())

#!/usr/bin/env python
"""
Create/delete random demo queues

usage: random_queues.py [-h] {create,delete}

positional arguments:
  {create,delete}

optional arguments:
  -h, --help       show this help message and exit

"""
import asyncio
import json
import logging
import os
import sys
from argparse import ArgumentParser
from random import sample
from typing import Optional

from dotenv import load_dotenv
from wxc_sdk.as_api import AsWebexSimpleApi
from wxc_sdk.as_rest import AsRestError
from wxc_sdk.locations import Location
from wxc_sdk.telephony import OwnerType
from wxc_sdk.telephony.callqueue import CallQueue, CallQueueCallPolicies, QueueSettings
from wxc_sdk.telephony.hg_and_cq import Agent

from integration_token import get_tokens

QUEUE_NAMES = ['word support',
               'dc escalation',
               'office support',
               'hr',
               'it',
               'registration',
               'billing',
               'payroll',
               'events',
               'travel']
LOCATION = 'Frisco'
FIRST_EXTENSION = 7500
AGENTS = 10


async def get_calling_users(api: AsWebexSimpleApi) -> list[str]:
    """
    get list of calling users

    ... the creative way by looking at assigned numbers
    :param api:
    :return: list of IDs of calling users
    """
    user_ids = set(number.owner.owner_id
                   for number in await api.telephony.phone_numbers(owner_type=OwnerType.people))
    return list(user_ids)


async def get_location(api: AsWebexSimpleApi) -> Optional[Location]:
    found = await api.locations.list(name=LOCATION)
    return found and found[0] or None


async def main():
    parser = ArgumentParser()
    parser.add_argument('action', choices=['create', 'delete'], default='create')
    args = parser.parse_args()
    create = args.action == 'create'

    # get environment variables from .env; required for integration parameters
    load_dotenv()

    async def create_or_delete_queue(name: str, extension: str) -> CallQueue:
        """
        Create/delete a queue
        """
        # shortcut to the queue API
        qapi = api.telephony.callqueue

        # does the queue already exist?
        queue = next((q for q in await qapi.list(location_id=location.location_id, name=name)
                      if q.name == name), None)
        if queue:
            if create:
                print(f'Queue "{name}" already exists; can\'t create', file=sys.stderr)
                return None
            else:
                # delete existing queue
                await qapi.delete_queue(location_id=location.location_id,
                                        queue_id=queue.id)
                return queue
        if not create:
            print(f'Queue "{name}" not found; can\'t delete', file=sys.stderr)
            return None

        # create a new queue with some random users
        agent_ids = sample(calling_users, min(len(calling_users), AGENTS))

        # settings for queue: defaults with list of agents to be added
        settings = CallQueue.create(
            name=name,
            call_policies=CallQueueCallPolicies.default(),
            queue_settings=QueueSettings.default(queue_size=10),
            agents=[Agent(agent_id=agent_id) for agent_id in agent_ids],
            extension=extension)

        # we want allow agents to join/leave the queue
        settings.allow_agent_join_enabled = True

        # agents can choose the queue caller ID as their own caller ID when placing calls
        settings.phone_number_for_outgoing_calls_enabled = True

        # actually create a queue with these settings
        # try up to three times
        for i in range(3):
            try:
                queue_id = await qapi.create(location_id=location.location_id, settings=settings)
            except AsRestError as e:
                print(f'Failed to create queue "{name}" ({extension}): {e}', file=sys.stderr)
                if e.status != 502 or i == 2:
                    raise
            else:
                # we are done here
                break

        print(f'Created queue "{name}" ({extension})', file=sys.stderr)

        # we want to return the actual queue
        # ... so, we need to get the details of the new queue
        queue = await qapi.details(location_id=location.location_id, queue_id=queue_id)
        return queue

    # get tokens from cache or create a new set of tokens using the integration defined in .env
    tokens = get_tokens()

    async with AsWebexSimpleApi(tokens=tokens) as api:
        # get calling users and target location; schedule concurrent execution
        calling_users, location = await asyncio.gather(get_calling_users(api), get_location(api))

        if not calling_users:
            print('No calling users', file=sys.stderr)
            exit(1)
        if not location:
            print(f'location "{LOCATION}" not found', file=sys.stderr)
            exit(1)

        calling_users: list[str]
        location: Location

        # generator for queue extensions starting at FIRST_EXTENSION
        extensions = (i + FIRST_EXTENSION for i in range(len(QUEUE_NAMES)))

        # for each name create or delete a queue with that name
        tasks = [create_or_delete_queue(name, next(extensions)) for name in QUEUE_NAMES]

        # schedule tasks for execution and wait for all results
        # ... and filter out None return values
        queues = [q for q in await asyncio.gather(*tasks, return_exceptions=True)
                  if q and not isinstance(q, Exception)]

    # done ... print a summary
    print(f'{args.action}d {len(queues)} queues', file=sys.stderr)

    # for the fun of it ...
    # ... print JSON representation of all queues we worked on to a file
    with open(os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.json'), mode='w') as file:
        print(json.dumps([json.loads(queue.json()) for queue in queues], indent=2), file=file)


if __name__ == '__main__':
    # enable DEBUG logging to a file; REST log shows all requests
    logging.basicConfig(filename=os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.log'),
                        filemode='w', level=logging.DEBUG)
    asyncio.run(main())

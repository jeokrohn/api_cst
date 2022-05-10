#!/usr/bin/env python
"""
Get all people details using sync calls vs. using asyncio
"""
import asyncio
from time import perf_counter

from wxc_sdk import WebexSimpleApi
from wxc_sdk.as_api import AsWebexSimpleApi
from wxc_sdk.tokens import Tokens

from integration_token import get_tokens

# get details with calling_data
CALLING_DATA = False


def people_details(tokens: Tokens):
    """
    Get details for all users using synchronous calls
    """

    def get_details(user_id: str):
        print('.', end='', flush=True)
        details = api.people.details(person_id=user_id, calling_data=CALLING_DATA)
        print('+', end='', flush=True)
        return details

    with WebexSimpleApi(tokens=tokens) as api:
        me = api.people.me()
        print(f'running as {me.display_name}({me.emails[0]})')
        user_list = list(api.people.list())
        print('Getting details...')
        start = perf_counter()
        all_details = [get_details(user_id=user.person_id) for user in user_list]
        print()
        print(f'Got details for {len(user_list)} users in {(perf_counter() - start) * 1000:.3f} ms')


async def async_people_details(tokens: Tokens):
    """
    Get details for all users using async calls
    """

    async def get_details(user_id: str):
        print('.', end='', flush=True)
        details = await api.people.details(person_id=user_id, calling_data=CALLING_DATA)
        print('+', end='', flush=True)
        return details

    async with AsWebexSimpleApi(tokens=tokens, concurrent_requests=10) as api:
        me = await api.people.me()
        print(f'running as {me.display_name}({me.emails[0]})')
        user_list = await api.people.list()
        start = perf_counter()
        # prepare tasks
        tasks = [get_details(user_id=user.person_id) for user in user_list]
        print('Getting details...')
        # schedule all tasks for execution and gather results
        all_details = await asyncio.gather(*tasks)
        print()
        print(f'Got details for {len(user_list)} users in {(perf_counter() - start) * 1000:.3f} ms')


if __name__ == '__main__':
    tokens = get_tokens()
    # get people details using sync calls
    people_details(tokens)
    # .. and the same using asyncio
    asyncio.run(async_people_details(tokens=tokens))

#!/usr/bin/env python
"""
Example script
read tokens from file or interactively obtain token by starting a local web server and open the authorization URL in
the local web browser
"""
import json
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from wxc_sdk import WebexSimpleApi
from wxc_sdk.integration import Integration
from wxc_sdk.scopes import parse_scopes
from wxc_sdk.tokens import Tokens
from yaml import safe_load, safe_dump

log = logging.getLogger(__name__)


def env_path() -> str:
    """
    determine path for .env to load environment variables from; based on name of this file
    :return: .env file path
    """
    return os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.env')


def yml_path() -> str:
    """
    determine path of YML file to persists tokens
    :return: path to YML file
    :rtype: str
    """
    return os.path.join(os.getcwd(), f'{os.path.splitext(os.path.basename(__file__))[0]}.yml')


def build_integration() -> Integration:
    """
    read integration parameters from environment variables and create an integration
    :return: :class:`wxc_sdk.integration.Integration` instance
    """
    client_id = os.getenv('INTEGRATION_CLIENT_ID')
    client_secret = os.getenv('INTEGRATION_CLIENT_SECRET')
    scopes = parse_scopes(os.getenv('INTEGRATION_SCOPES'))
    redirect_url = 'http://localhost:6001/redirect'
    if not all((client_id, client_secret, scopes)):
        raise ValueError('failed to get integration parameters from environment')
    return Integration(client_id=client_id, client_secret=client_secret, scopes=scopes,
                       redirect_url=redirect_url)


def get_tokens() -> Optional[Tokens]:
    """
    Tokens are read from a YML file. If needed an OAuth flow is initiated.

    :return: tokens
    :rtype: :class:`wxc_sdk.tokens.Tokens`
    """

    # load environment variables from .env
    path = env_path()
    log.info(f'reading {path}')
    load_dotenv(env_path())

    integration = build_integration()
    tokens = integration.get_cached_tokens_from_yml(yml_path=yml_path())
    return tokens


def main():
    logging.basicConfig(level=logging.DEBUG)

    tokens = get_tokens()

    # use the tokens to get identity of authenticated user
    api = WebexSimpleApi(tokens=tokens)
    me = api.people.me()
    print(f'authenticated as {me.display_name} ({me.emails[0]}) ')


if __name__ == '__main__':
    main()

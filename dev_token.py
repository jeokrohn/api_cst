#!/usr/bin/env python
"""
Example for reading developer access token from  environment variable
"""
import os

from dotenv import load_dotenv


def main():
    # load .env file
    load_dotenv()

    # after reading .env file all variables defined in the file are accessible as environment variables
    access_token = os.getenv('WEBEX_TOKEN')
    print(f'Access token from environment: {access_token}')


if __name__ == '__main__':
    main()

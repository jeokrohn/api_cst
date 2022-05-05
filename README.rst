Example code for CST session on Webex APIs in May 2022
======================================================

Prepare the environment
-----------------------

* First you have to make sure that you have Python 3.0 installed. This is the minimum version for the  `wxc-sdk` module
  used in the examples.

* Then you need to install `pipenv` to manage your virtual environments. Installation instructions can be found here:
  https://pipenv.pypa.io/en/latest/

* create a working directory and change to that directory:

    | ``mkdir api_cst``
    | ``cd api_cst``

* clone the Git repository to this directory or download the repository and unzip it

* change to the base directory of the repository; the one where `Pipfile` lives

* install requirements

    | ``pipenv install``

Now, your test environment should be ready

Examples
--------

* ``dev_token.py``: reading developer tokens from environment variables
* ``integration_token.py``: work with cached integration tokens
* ``list_locations_direct.py``: list locations, crafting the REST request directly
* ``list_locations_sdk.py``: list locations using the ``wxc_sdk`` module
* ``list_locations_sdk.py``: list locations using the ``wxc_sdk`` module and cached tokens
* ``people_details.py``: get user details synchronously and using asyncio to compare performance




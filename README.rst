Example code for Introduction into WxC APIs
===========================================

Prepare the environment
-----------------------

* First you have to make sure that you have Python 3.9 installed. This is the minimum version for the  `wxc-sdk` module
  used in the examples. Python releases can be downloaded here: https://www.python.org/downloads/. For Mac users I would
  recommend to install Python using Homebrew as described here: https://docs.python-guide.org/starting/install3/osx/.

* Then you need to install `pipenv` to manage your virtual environments. Installation instructions can be found here:
  https://pipenv.pypa.io/en/latest/

* create a working directory and change to that directory:

    | ``mkdir api_cst``
    | ``cd api_cst``

* clone this Git repository to this directory or download the repository and unzip it

* change to the base directory of the repository; the one where ``Pipfile`` lives

* install requirements

    | ``pipenv install``

Now, your test environment should be ready

Examples
--------

* ``dev_token.py``: reading developer tokens from environment variable or ``.env`` file
* ``list_locations_direct.py``: list locations, crafting the REST request directly
* ``list_locations_sdk.py``: list locations using the ``wxc_sdk`` module
* ``integration_token.py``: work with cached integration tokens
* ``list_locations_sdk_int_tokens.py``: list locations using the ``wxc_sdk`` module and cached tokens
* ``people_details.py``: get user details synchronously and using asyncio to compare performance
* ``queue_helper.py``: command line tool to manage Webex Calling call queues
* ``read_queues.py``: reading call queue details, printing summary to stdout an creating a CSV file
* ``random_queues.py``: creating random call queues for a demo; shows call queue creation




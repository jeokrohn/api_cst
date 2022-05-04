Example code for CST session on Webex APIs in May 2022
======================================================

Prepare the environment
-----------------------

* First you have to make sure that you have Python 3.0 installed. This is the minimum version for the  `wxc-sdk` module
used in the examples.

* Then you need to install `pipenv` to manage your virtual environments. Installation instructions can be found here:
  https://pipenv.pypa.io/en/latest/

* create a working directory and change to that directory:
  .. code-block::

        mkdir api_cst
        cd api_cst
* clone the Git repository to this directory or download the repository and unzip it

* change to the base directory of the repository; the one where `Pipfile` lives

* install requirements
  .. code-block::

        pipenv install

Now, your test environment should be ready

Examples
--------

Handling developer tokens
.........................

Source: ``dev_token.py``

.. |calling_users.py| replace:: ``calling_users.py``

.. literalinclude:: dev_token.py
    :linenos:

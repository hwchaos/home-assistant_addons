"""
This file is for development purposes.
The deployment version won't take it to the container. Instead, run.sh will
generate one with the options provided by bashio.
"""

DEBUG_MODE = True
CUSTOM_PORT = 514
ENDPOINT_1 = "states/input_boolean.doorman"
ENDPOINT_2 = "states/input_boolean.doorman"
TO_SEEK_1 = 'r"Authenticated"'
TO_SEEK_2 = 'r"Connection closed"'
PAYLOAD_1 = '{"state": "on"}'
PAYLOAD_2 = '{"state":"off"}'

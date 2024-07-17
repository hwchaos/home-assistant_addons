"""
This script listens to logs provided by clients via UDP on the configured port

When a pattern matches the content of the received log, a post request is made
to the Home Assistant API.

forked from
Mauricio Vidal, 2022
https://github.com/MrMauro/home-assistant_addons

The part related to the "Syslog Server" is based on:
https://gist.github.com/marcelom/4218010

"""

import logging
import socketserver
import os
import re
import json
from requests import post
from config import (
    DEBUG_MODE,
    CUSTOM_PORT,
    ENDPOINT_1,
    ENDPOINT_2,
    TO_SEEK_1,
    TO_SEEK_2
)

# Server address
CUSTOM_HOST = '0.0.0.0'

# Request header using the Home Assistant Token.
headers = {
    'Authorization': 'Bearer ' + os.environ.get('SUPERVISOR_TOKEN'),
    'content-type': 'application/json',
}

# URLs for the endpoints
endpoint_1_url = 'http://supervisor/core/api/' + ENDPOINT_1
endpoint_2_url = 'http://supervisor/core/api/' + ENDPOINT_2

# Payload to send
payload_template = {"state": "payload"}

# Own logger setup (This is not related to the Syslog server)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger_sl2ha = logging.getLogger(__name__)

# Greet
logger_sl2ha.info("Syslog to Home Assistant has started using the following configuration:\n\tDebug: %s|%s\n\tPort: %s|%s\n\tEndpoint 1: %s|%s\n\tEndpoint 2: %s|%s\n\tSeek 1: %s|%s\n\tSeek 2: %s|%s", type(DEBUG_MODE), DEBUG_MODE, type(CUSTOM_PORT), CUSTOM_PORT, type(endpoint_1_url), endpoint_1_url, type(endpoint_2_url), endpoint_2_url, type(TO_SEEK_1), TO_SEEK_1, type(TO_SEEK_2), TO_SEEK_2)

# Own-logger level setup
if str(DEBUG_MODE) == 'true' or str(DEBUG_MODE) == 'True':
    logger_sl2ha.setLevel(logging.DEBUG)
    logger_sl2ha.info("Debug mode has been enabled")
else:
    logger_sl2ha.setLevel(logging.INFO)
    logger_sl2ha.info("Debug mode has been disabled")

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """
    This is an extension of the class to implement a handler.
    """
    def handle(self):
        """
        On every log received, the content will be inspected to check the
        existence of certain text. When it matches, a post request is made to
        the configured Home Assistance API url using the pertinent payload.
        """
        # The data is received.
        data = bytes.decode(self.request[0].strip())

        # This is the address of the device that provided the log
        source = self.client_address[0]

        # Log the incoming data
        logger_sl2ha.debug("%s has a new log with data:\n%s", source, str(data))

        # Check for matches using regular expressions
        if re.search(TO_SEEK_1, data):
            logger_sl2ha.info("%s: matched pattern: %s", source, TO_SEEK_1)
            payload = self.create_payload(data)
            if payload:
                response = post(url=endpoint_1_url, headers=headers, json=payload)
                logger_sl2ha.debug("Response from API at: %s with code: %s, data: %s", endpoint_1_url, response.status_code, response.text)

        elif re.search(TO_SEEK_2, data):
            logger_sl2ha.info("%s: matched pattern: %s", source, TO_SEEK_2)
            payload = self.create_payload(data)
            if payload:
                response = post(url=endpoint_2_url, headers=headers, json=payload)
                logger_sl2ha.debug("Response from API at: %s with code: %s, data: %s", endpoint_2_url, response.status_code, response.text)

    def create_payload(self, data):
        """
        Creates the payload from the syslog message.
        """
        try:
            # Example logic to extract necessary information from data
            # Replace with your actual logic to generate the payload
            # For example, extracting "payload" from the data
            extracted_payload = "payload"

            # Construct the payload dictionary
            payload = {"state": extracted_payload}

            logger_sl2ha.debug("Created payload: %s", payload)
            return payload
        except Exception as e:
            logger_sl2ha.error("Failed to create payload: %s", e)
            return {}

if __name__ == "__main__":
    try:
        server = socketserver.UDPServer(
            server_address=(CUSTOM_HOST, CUSTOM_PORT),
            RequestHandlerClass=SyslogUDPHandler,
        )
        server.serve_forever(
            poll_interval=0.5
        )
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")

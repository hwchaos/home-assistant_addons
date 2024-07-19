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

# Own logger setup (This is not related to the Syslog server)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger_sl2ha = logging.getLogger(__name__)

# Greet
logger_sl2ha.info("Syslog to Home Assistant has started using the following configuration:\n\tDebug: %s|%s\n\tPort: %s|%s\n\tEndpoint 1: %s|%s\n\tEndpoint 2: %s|%s", type(DEBUG_MODE), DEBUG_MODE, type(CUSTOM_PORT), CUSTOM_PORT, type(endpoint_1_url), endpoint_1_url, type(endpoint_2_url), endpoint_2_url)

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
        for endpoint, config in [
            (endpoint_1_url, TO_SEEK_1),
            (endpoint_2_url, TO_SEEK_2)
        ]:
            match = re.search(config["pattern"], data)
            if match:
                logger_sl2ha.info("%s: matched pattern: %s", source, config["pattern"])
                payload = self.create_payload(config["payload_template"], match)
                if payload:
                    response = post(url=endpoint, headers=headers, json=payload)
                    logger_sl2ha.debug("Response from API at: %s with code: %s, data: %s", endpoint, response.status_code, response.text)

    def create_payload(self, template, match):
        """
        Creates the payload from the syslog message using a template.
        """
        try:
            # Extract the relevant data from the match object
            extracted_value = match.group(1)  # Adjust group index as necessary

            # Format the payload template with the extracted value
            payload_str = template.format(extracted=extracted_value)
            payload = json.loads(payload_str)  # Convert string to JSON

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

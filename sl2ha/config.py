# config.py

# Set debug mode
DEBUG_MODE = True

# Custom port
CUSTOM_PORT = 514

# Endpoints for Home Assistant API
ENDPOINT_1 = "path/to/endpoint1"
ENDPOINT_2 = "path/to/endpoint2"

# Define regex patterns and payload templates
TO_SEEK_1 = {
    "pattern": r"<\d+:(\w+)\(\d+\)>",  # Example regex pattern
    "payload_template": '{"state": "{extracted}"}'
}

TO_SEEK_2 = {
    "pattern": r"Connection closed: (\w+)",  # Another example regex pattern
    "payload_template": '{"state": "{extracted}"}'
}

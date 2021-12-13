#!/usr/bin/env python3

import socket
import sys
import argparse
import json

HOST = 'localhost'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

settings = {
    'activated_smoke': False,
    'activated_lights_g': True,
    'activated_lights_party':  False,
    'music': 'techno',
    'smoke_interval': 120 # steps: 60, 120, 180, 240, off
}

message = {
    'type': 'log',
    'message': 'testmessage error 123',
    'settings': settings
}



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(json.dumps(message).encode())
    exit()



# #!/usr/bin/env python3

# import socket
# import sys
# import argparse

# HOST = 'localhost'  # The server's hostname or IP address
# PORT = 65432        # The port used by the server

# parser = argparse.ArgumentParser(description='Short sample app')

# parser.add_argument('message', action="store", type=str)

# args = parser.parse_args()

# print(parser.parse_args())

# if args.message != "start" and args.message != "stop" and args.message != "quit":
#     raise Exception("Not a valid argument")


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(args.message.encode())
#     exit()

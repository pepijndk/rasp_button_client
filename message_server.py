#!/usr/bin/env python3

import socket, sys, argparse

HOST = '192.168.0.114'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('message', action="store", type=str)

args = parser.parse_args()

print(parser.parse_args())

if args.message != "start" and args.message != "stop" and args.message != "quit":
    raise Exception("Not a valid argument")
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(args.message.encode())
    exit();
        
    

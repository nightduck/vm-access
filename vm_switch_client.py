#!/usr/bin/env python3
import socket

#This file connects to the server at socket 52831, at either localhost (if this is running on
#the host) or the IP address specified during installation (if this is running on the guest).
#After connecting, this program sends the command "switch" and immediately disconnects and
#terminates. It's reccomeneded to map a hotkey to run this program, and then that hotkey would
#appear to be a kvm toggle switch

HOST = "192.168.1.4"
PORT = 57831

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(b'toggle')
s.close()
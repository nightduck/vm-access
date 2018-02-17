#!/usr/bin/env python3
import libvirt
import sys
import socket
import socketserver

#This file sets up a TCP server listening on port 52831. Anytime it receives a command to switch,
#it'll toggle the keyboard and mouse (and any other devices specified during installation)
#between host and VM.
#!/usr/bin/env python3
import socket
import socketserver
import subprocess
import os

# This file sets up a TCP server listening on port 52831. Anytime it receives a command to switch,
# it'll toggle the keyboard and mouse (and any other devices specified during installation)
# between host and VM.


def change_usb_state(cmd, vm, device):
    global state

    # Cmd can be "detach" if sent from host, "attach" if sent from guest, or "toggle" as a generic command
    if cmd == state: return
    if cmd == "toggle":
        cmd = "attach" if state == "detach" else "detach"

    # Make a tmp xml file using the device (eg 48d6:fe8b)
    xml_path = '/tmp/device-{}.xml'.format(device)
    if not os.path.exists(xml_path):
        with open(xml_path, 'w+') as fp:
            fp.write("""
                <hostdev mode='subsystem' type='usb'>
                    <source>
                        <vendor id='0x{}'/>
                        <product id='0x{}'/>
                    </source>
                </hostdev>
            """.format(*device.split(':')))

    # Call virsh to attach or remove the device, and update state
    success = subprocess.call(['virsh', cmd+'-device', vm, xml_path]) == 0

    # If successful, update the state
    if success: state = cmd
    return success


# Note: This handler only supports toggling 2 state host<>guest with a single VM. If there's every a need
# to support multiple VMs, this will have to be modified
class CmdHandler(socketserver.BaseRequestHandler):
    def handle(self):
        cmd = self.request.recv(1024).strip().decode('utf-8')
        print("{} said: {}".format(self.client_address[0], cmd))
        if cmd in ["detach", "attach", "toggle"]:
            print("  command valid")
            for dev in devices:
                print("{}ing {}".format(cmd, dev))
                if change_usb_state(cmd, vms[0], dev):
                    print("    Success")
                else:
                    print("    Failed")


HOST, PORT = "localhost", 57831
state = 'detach'                        # The last command executed (ie detach if currently on host, attach if on guest)
devices = ("046d:c332", "1b1c:1b33")    # List of USB devices to toggle. Run lsusb to find the IDs of yours
vms = ("win10",)                        # NOTE: This program only uses the first item in this list

server = socketserver.TCPServer((HOST, PORT), CmdHandler)
server.serve_forever()


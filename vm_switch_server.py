#!/usr/bin/env python3
import socket
import socketserver
import subprocess
import os
from time import sleep
import threading

# This file sets up a TCP server listening on port 52831. Anytime it receives a command to switch,
# it'll toggle the keyboard and mouse (and any other devices specified during installation)
# between host and VM.


# This yanks the device from whatever vm it may be stuck in. Sometimes vm's think they have a device, but the host is
# controlling them and they need a sort of hard reboot
def pull_device(device):
    # subprocess.call requires an xml file, so make a tmp xml file using the device numbers (eg 48d6:fe8b)
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

    for vm in vms:
        try:
            # Sometimes the guest will have multiple instances of a device. Remove all until you can't remove no more
            # The check_output method will throw an error when there's nothing to detach
            while True:
                subprocess.check_output(['virsh', 'detach-device', vm, xml_path])
        except subprocess.CalledProcessError:
            pass

def change_usb_state(cmd, vm, device):
    # Cmd can be "detach" if sent from host, "attach" if sent from guest, or "toggle" as a generic command
    if cmd == state: return
    if cmd == "toggle":
        cmd = "attach" if state == "detach" else "detach"

    # subprocess.call requires an xml file, so make a tmp xml file using the device numbers (eg 48d6:fe8b)
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

    # Call virsh to attach or remove the device and verify the call worked.
    try:
        subprocess.check_output(['virsh', cmd+'-device', vm, xml_path])
        print("Output printed")
        return True
    except subprocess.CalledProcessError:
        return False

    # If not, yank back all instances of this device from this VM and try again. It likely this is only needed when
    # attaching failed
    try:
        # Remove all until you can't remove no more
        while True:
            subprocess.check_output(['virsh', 'detach-device', vm, xml_path])
    except TypeError:
        subprocess.call(['virsh', cmd+'-device', vm, xml_path])


# Note: This handler only supports toggling 2 state host<>guest with a single VM. If there's every a need
# to support multiple VMs, this will have to be modified
class CmdHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global state
        cmd = self.request[0].strip().decode('utf-8')
        socket = self.request[1]
        print("{} said: {}".format(self.client_address[0], cmd))
        if cmd in ["detach", "attach", "toggle"]:
            print("  command valid")
            success = True

            for dev in devices:
                print("{}ing {}".format(cmd, dev))
                if not change_usb_state(cmd, vms[0], dev):
                    success = False

            if not success:
                for dev in devices:
                    pull_device(dev)
                state = 'detach'
            else:
                state = ("detach" if state == "attach" else "attach") if cmd == "toggle" else cmd


def poll():
    while True:
        print("state={}".format(state))
        sleep(3)

HOST, PORT = "0.0.0.0", 57831
state = 'detach'                        # The last command executed (ie detach if currently on host, attach if on guest)
devices = ("046d:c332", "1b1c:1b33")    # List of USB devices to toggle. Run lsusb to find the IDs of yours
vms = ("win10",)                        # NOTE: This program only uses the first item in this list

# Pull all devices from all VMs for a clean service startup
for d in devices:
    pull_device(d)

threading.Thread(target=poll).start()

server = socketserver.UDPServer((HOST, PORT), CmdHandler)
server.serve_forever()

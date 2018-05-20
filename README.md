### NOTICE
This repository is no longer maintained. It has been superseded by the C++ based [virtkvm project](https://github.com/madstk1/virtkvm). You can find my fork [here](https://github.com/nightduck/virtkvm).

## Installation instructions

To install, first run lsusb and look for the device numbers. Sample output below. The IDs in bold are the ones I want
to pass.

<pre>
    Bus 006 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 003 Device 002: ID 0b05:17cb ASUSTek Computer, Inc. Broadcom BCM20702A0 Bluetooth
    Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 006: ID <b>046d:c332</b> Logitech, Inc. G502 Proteus Spectrum Optical Mouse
    Bus 001 Device 007: ID <b>1b1c:1b33</b> Corsair
</pre>

Then, use these values to fill the tuple on the line that says devices = ... . Also, change the IP address if you want.
As it's currently set up, it'll listen on all networks it's connected to (eg your smartphone could switch your
peripherals). Not a very secure approach, but if your guest and host have a shared network between them that only they
can see, set it to that IP address. 
       
TODO: A process to install the server has not been implemented yet. You can follow the guide from the [code this is
based on](https://rokups.github.io/#!pages/kvm-hid.md) to manually create a system service. 

The client script should be copied to both the host and guest. It's most convenient to map this to a keyboard shortcut.
This varies widely in Linux depending on your desktop environment so you're on your own there. Just map it to run

    /path/to/vm_switch_client.py
       
On my Windows guest, I just put a shortcut to the program on my desktop, right click the shortcut > Properties, and
there's an option to add a hotkey. This is pretty slow (~3 sec), so if you know a better way, let me know. 
       
### Prerequisites

 * python3 (all of the modules used are available in 2.7, so if you want to port it, power to you)
 * libvirt python module

### Troubleshooting
If your hotkey stops responding, try opening virt-manager, manually removing the USB devices (if connected) and running

    sudo systemctl restart vm_switch.service
    
    
### Credits

The server is inspired by the code [here](https://rokups.github.io/#!pages/kvm-hid.md), but has been edited to use a
regular TCP port, instead of unix domain sockets. So the Windows guest can access it without having to do the weird
ssh thing

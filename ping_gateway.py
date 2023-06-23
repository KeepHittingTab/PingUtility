import time
import socket
import struct
import threading
import ipaddress
import os
import re
import subprocess
from ping3 import verbose_ping
from pystray import MenuItem as item
import pystray
from PIL import Image

icon_online = Image.open('green.ico')
icon_offline = Image.open('red.ico')

def get_default_gateway():
    if os.name == 'nt':  # For Windows
        proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline()
            if line != b'':
                line = line.decode('utf8').strip()
                if "Default Gateway" in line:
                    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line) # this will grab the IP
                    if ip:
                        return ip[0]
            else:
                break
    else:  # For Linux/Mac
        proc = subprocess.Popen('route -n get default', stdout=subprocess.PIPE, shell=True)
        while True:
            line = proc.stdout.readline()
            if line != b'':
                line = line.decode('utf8').strip()
                if line.startswith('gateway:'):
                    return line.split(' ')[1]
            else:
                break

def action_exit(icon, item):
    icon.stop()

def pinger(icon):
    default_gateway = get_default_gateway()
    while True:
        try:
            verbose_ping(default_gateway, timeout=1, count=1)
            icon.icon = icon_online
        except Exception:
            icon.icon = icon_offline
        icon.update_menu()
        time.sleep(1)
        new_default_gateway = get_default_gateway()
        if default_gateway != new_default_gateway:
            default_gateway = new_default_gateway

def setup(icon):
    icon.visible = True
    threading.Thread(target=pinger, args=(icon,), daemon=True).start()

icon = pystray.Icon("name", icon_online, "My System Tray Icon", menu=pystray.Menu(item('Exit', action_exit)))

icon.run(setup)

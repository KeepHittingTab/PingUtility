import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import threading
import socket

def get_default_gateway():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            default_gateway_ip = s.getsockname()[0]
            return default_gateway_ip
    except socket.error as e:
        print(f"Error retrieving default gateway: {str(e)}")
        return None

def ping_gateway():
    default_gateway_ip = get_default_gateway()
    if default_gateway_ip:
        try:
            output = subprocess.check_output(['ping', '-n', '1', default_gateway_ip], timeout=1)
            print(output.decode())
            if 'TTL=' in output.decode():
                update_status_icon('green')
            else:
                update_status_icon('red')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(str(e))
            update_status_icon('red')
    else:
        update_status_icon('red')

def update_status_icon(color):
    global icon
    icon_path = 'green.ico' if color == 'green' else 'red.ico'
    icon.icon = Image.open(icon_path)

def monitor_thread():
    while True:
        ping_gateway()
        threading.Event().wait(1)

def exit_action(icon, item):
    global monitoring_thread
    monitoring_thread.stop()
    icon.stop()

menu = (item('Exit', exit_action),)

initial_icon = Image.open('red.ico')

icon = pystray.Icon("Ping Monitor", initial_icon, menu=menu)

monitoring_thread = threading.Thread(target=monitor_thread)
monitoring_thread.start()

icon.run()

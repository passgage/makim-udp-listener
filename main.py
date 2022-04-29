import socket
import os
import requests
import json

# API_ADDR = os.environ["API_ADDR"] #"http://127.0.0.1:3000/api/v1/panel_cards"
API_ADDR = "http://95.0.169.125:3000/api/v1/panel_cards"
# IP = os.environ["BINDING"]


BUSY = False


def parse(buffer, ip):
    serial = buffer[3:7]
    panel_no = buffer[7:10]
    reader = buffer[10:12]
    card_no = buffer[21:31]
    return {
        "serial": serial.decode(),
        'panel_no': int(panel_no),
        'reader': int(reader),
        'card_no': int(card_no),
        'ip': ip
    }

def send_to_api(access_info):
    try:
        global BUSY
        BUSY = True
        data = json.dumps(access_info)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resp = requests.post(API_ADDR, data=data, headers=headers)
        print(f'response: {resp.status_code}')
    except Exception as ex:
        print(ex.args[0])
    finally:
        BUSY = False






def listen():
    global BUSY
    udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp.bind(("", 11011))
    print("listenning on {}".format(11011))
    while True:
        if not BUSY:
            msg, adr = udp.recvfrom(1024)
            if msg.startswith(b'%CD'):
                print(f'incoming buffer: {msg}')
                parsed = parse(msg, adr[0])
                print(parsed)
                send_to_api(parsed)


if __name__ == '__main__':
    listen()
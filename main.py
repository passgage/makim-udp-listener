import socket
import requests
import json
from activity import Activity
from datetime import datetime
from threading import Thread


# API_ADDR = os.environ["API_ADDR"] #"http://127.0.0.1:3000/api/v1/panel_cards"
API_ADDR = "http://95.0.169.125:3000/api/v1/panel_cards"
# IP = os.environ["BINDING"]


ACTIVITIES = []


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


def can_be_sent(card_no):
    global ACTIVITIES
    acts = [act for act in ACTIVITIES if act.card_no == card_no]
    if len(acts) > 0:
        diff = (datetime.now() - acts[-1].activity_time).total_seconds()
        if diff < 3:
            print(f"door trigger cannot be sent. time delta: {diff} secs")
            return False
        print(f"door trigger can be sent. time delta: {diff} secs")
        return True
    else:
        if len(ACTIVITIES) > 200:
            ACTIVITIES = ACTIVITIES[1:]
        print("door trigger can be sent. first occurrence of this card")
        return True


def send_action(access_info):
    try:
        data = json.dumps(access_info)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resp = requests.post(API_ADDR, data=data, headers=headers)
        print(f'response: {resp.status_code}')
    except Exception as ex:
        print(ex.args[0])


def send_to_api(access_info):
    try:
        if can_be_sent(access_info["card_no"]):
            t = Thread(target=send_action, args=(access_info,))
            t.start()
        ACTIVITIES.append(Activity(activitiy_time=datetime.now(), card_no=access_info["card_no"]))
    except Exception as ex:
        print(ex.args[0])


def listen():
    udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp.bind(("", 11011))
    print("listening on {}".format(11011))
    while True:
        msg, adr = udp.recvfrom(1024)
        if msg.startswith(b'%CD'):
            print(f'incoming buffer: {msg}')
            parsed = parse(msg, adr[0])
            if parsed['card_no'] != 0:
                print(parsed)
                send_to_api(parsed)


if __name__ == '__main__':
    listen()

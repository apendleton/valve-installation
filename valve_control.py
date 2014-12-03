import json, urllib2, serial
from websocket import create_connection

port = '/dev/tty.usbmodem641'

ard = serial.Serial(port, 115200, timeout=5)

def set_valve(valve_number, state):
    message = chr(valve_number | (int(state) << 3))
    ard.write(message)

def get_states(distances):
    states = [False] * 6
    for i, stick in enumerate(distances):
        if any([height['on'] for height in stick]):
            states[i] = True
    return states

def update_valves():
    data = json.load(urllib2.urlopen('http://localhost:5000/status'))
    states = get_states(data['distances'])
    print "Updating states to", states
    for valve, state in enumerate(states):
        set_valve(valve, state)

def start_ws():
    ws = create_connection("ws://localhost:5000/changes")
    
    update_valves()

    while True:
        ws.recv()
        update_valves()


if __name__ == "__main__":
    start_ws()
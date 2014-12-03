import json, requests
from websocket import create_connection

def get_states(distances):
    states = ['off'] * 6
    for i, stick in enumerate(distances):
        if stick[1]['on']:
            states[i] = 'high'
        elif stick[0]['on'] and not stick[1]['on']:
            states[i] = 'low'
    return states

def trigger_state(stick, state):
    print('setting', stick, 'to', state)

def all_off():
    print('setting everything to off')

current_states = ['off'] * 6
def update_osc():
    global current_states

    data = requests.get('http://localhost:5000/status').json()
    states = get_states(data['distances'])
    print("Updating states to", states)
    
    everything_off = True
    for stick, state in enumerate(states):
        if current_states[stick] != state:
            trigger_state(stick, state)
            current_states[stick] = state
        if state != 'off':
            everything_off = False

    if everything_off:
        # just to make sure everything is how it's supposed to be, force-kill everything
        all_off()


def start_ws():
    ws = create_connection("ws://localhost:5000/changes")
    
    update_osc()

    while True:
        ws.recv()
        update_osc()


if __name__ == "__main__":
    start_ws()
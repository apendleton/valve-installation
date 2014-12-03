import json, requests
from websocket import create_connection

from pythonosc import osc_message_builder
from pythonosc import udp_client

from oset import oset

QLAB_IP = '192.168.2.110'

def get_states(distances):
    states = ['off'] * 6
    for i, stick in enumerate(distances):
        if stick[1]['on']:
            states[i] = 'high'
        elif stick[0]['on'] and not stick[1]['on']:
            states[i] = 'low'
    return states

osc_client = udp_client.UDPClient(QLAB_IP, 53000)
def send_osc(qnum):
    print("sending q", qnum)
    msg = osc_message_builder.OscMessageBuilder(address = '/cue/' + str(qnum) + '/start')
    msg = msg.build()
    osc_client.send(msg)

offsets = {'high': (10001, 10002), 'low': (10003, 10004), 'off': (10005,)}
state_history = oset()
def trigger_state(stick, state, sound_only=False):
    print('setting', stick, 'to', state)
    soffsets = offsets[state][:1] if sound_only else offsets[state]
    for o in soffsets:
        send_osc((stick * 5) + o)

    if state in ('low', 'high'):
        state_tuple = (stick, state)
        state_history.discard(state_tuple)
        state_history.add(state_tuple)
    else:
        state_history.discard((stick, 'low'))
        state_history.discard((stick, 'high'))

        # re-trigger the last one
        if len(state_history) > 0:
            trigger_state(*state_history[-1], sound_only=True)

def all_off():
    print('setting everything to off')
    send_osc(10031)

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
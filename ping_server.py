#!/usr/bin/python

from gevent.monkey import patch_all
patch_all()

import serial, operator, gevent
from gevent.event import Event
from gevent import Greenlet

# change to your Arduino serial device
port = '/dev/tty.usbmodem411'

distance = [list((100, 100)) for i in xrange(6)]
real_on = [list((False, False)) for i in xrange(6)]
fake_on = [list((False, False)) for i in xrange(6)]
threshold = 50
min_reading = 6

notify = Event()
pending_changes = []
changes_to_notify = []
most_recent_on = (None, None)
kill_greenlet = Greenlet()

def notify_waiting():
    global changes_to_notify
    global pending_changes

    changes_to_notify = pending_changes
    pending_changes = []
    print distance
    notify.set()
    notify.clear()

def arduino_thread():
    ard = serial.Serial(port, 115200, timeout=5)
    global distance
    global pending_changes
    global changes_to_notify
    global most_recent_on
    global kill_thread

    while True:
        # Serial read section
        msg = ard.readline().strip()
        if msg:
            try:
                stick, height, value = map(int, msg.split('/'))
            except:
                continue

            if value < min_reading:
                # misread
                continue

            current = distance[stick][height]
            distance[stick][height] = value

            current_on = current < threshold
            old_on = real_on[stick][height]

            if current_on != old_on:
                real_on[stick][height] = current_on

                if current_on == True:
                    fake_on[stick][height] = True
                    most_recent_on = (stick, height)
                    kill_greenlet.kill()

                    # if we had fake-kept any of the surrounding ones hot, turn them off
                    for ostick in xrange(6):
                        if ostick != stick:
                            fake_on[ostick] = list(real_on[ostick])
                else:
                    # this is when we fake the off state if necessary

                    # are the ones in any direction hot?
                    if (stick < 5 and any(real_on[stick + 1])) or (stick > 0 and any(real_on[stick - 1])) or real_on[stick][0 if height == 1 else 1]:
                        fake_on[stick][height] = False
                    else:
                        # otherwise we keep it hot
                        # and if it's on the ends and nothing else is on, we set a timer
                        if stick in (0, 5) and not any(reduce(operator.add, real_on)) and not any(reduce(operator.add, fake_on[1:5])):
                            kill_thread = gevent.spawn_later(2, kill_stale_fakes)


                pending_changes.insert(0, (stick, height))
            
            if height == 1 and len(pending_changes):
                notify_waiting()

def kill_stale_fakes():
    for stick in xrange(6):
        for height in xrange(2):
            if fake_on[stick][height] and not real_on[stick][height]:
                fake_on[stick][height] = False
                pending_changes.insert(0, (stick, height))
    if len(pending_changes):
        notify_waiting()

import threading
t = threading.Thread(target=arduino_thread, args=())
t.daemon = True
t.start()

# flask app
from flask import Flask, jsonify
from flask_sockets import Sockets
import json

app = Flask(__name__)
sockets = Sockets(app)

@app.route('/status')
def status():
    return jsonify({
        'distances': [[
            {'inches': distance[j][i], 'on': fake_on[j][i], 'real_on': real_on[j][i]}
                for i in xrange(2)] for j in xrange(6)],
        'most_recent_on': {'stick': most_recent_on[0], 'height': most_recent_on[1]}
    })

@app.route('/reset')
def reset():
    kill_stale_fakes()
    return jsonify({'success': True})

@sockets.route('/changes') 
def changes(ws):
    while True: 
        notify.wait()
        change_set = [
            {'stick': cell[0], 'height': cell[1], 'distance': distance[cell[0]][cell[1]], 'on': fake_on[cell[0]][cell[1]], 'real_on': real_on[cell[0]][cell[1]]}
            for cell in changes_to_notify
        ]
        ws.send(json.dumps({'changes': change_set, 'most_recent_on': {'stick': most_recent_on[0], 'height': most_recent_on[1]}}))

@app.route('/monitor')
def monitor():
    return app.send_static_file('monitor.html')

if __name__ == '__main__':
    app.run()
from collections import OrderedDict
from itertools import cycle
import sys

# build the pitch table
note_names = ['A', 'A#/Bb', 'B', 'C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab']
note_cycle = cycle(note_names)

piano = []
onumber = 0
for i in range(1, 89):
    note = note_cycle.next()

    if note == 'C':
        onumber += 1

    piano.append({
        'number': i,
        'name': [n + str(onumber) for n in note.split('/')],
        'freq': (2 ** ((i - 49.0) / 12)) * 440
    })

# invert it
freqs = {}
for key in piano:
    for name in key['name']:
        freqs[name] = key['freq']

# look at arguments for pitch names and build samples
from wavebender import *

flist = []
requested = sys.argv[1:]
amp = 0.8 / len(requested)
for arg in requested:
    flist.append(sine_wave(freqs[arg], amplitude=amp))

channels = (tuple(flist),)

nframes = 44100 * 10

samples = compute_samples(channels, nframes)
write_wavefile(sys.stdout, samples, nchannels=1, nframes=nframes)
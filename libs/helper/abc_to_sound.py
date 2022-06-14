import re
import numpy as np

import wave
import struct

from graiax import silkcoder

class Parser:
    note_dict = { 
        "C": 0, 
        "D": 2, 
        "E": 4, 
        "F": 5, 
        "G": 7, 
        "A": 9, 
        "B": 11,
        "c": 12,
        "d": 14,
        "e": 16,
        "f": 17,
        "g": 19,
        "a": 21,
        "b": 23,
    }
    regex_note = r"(?:\^|=|_|\^\^|__|#|♯|♭)?[A-Ga-gz][\'`,]*\/*\d*"
    regex_chord = r"\[(" + regex_note + r")+\]\/*\d*"
    #regex_chord_or_note = r"(?:" + regex_chord + r")|(?:" + regex_note + r")"
    #regex_broken = r"(?:" + regex_chord_or_note + r"<+|>+" + regex_chord_or_note
    #regex_slurs = regex_chord_or_note + r"(?:-" + regex_chord_or_note + r")+"
    tokens = [
        ("CHORD", regex_chord),
        ("NOTE", regex_note)
        #("BROKEN", regex_broken),
        #("SLURS", regex_slurs),
    ]
    regex = '|'.join('(?P<%s>%s)' % pair for pair in tokens)

    regex_note_grouped = r"(?P<acc>\^|=|_|\^\^|__|#|♯|♭)?(?P<pitch>[A-Ga-gz])(?P<ext>[\'`,]*)(?P<len>\/*\d*)"
    re_note = re.compile(regex_note_grouped)
    temp_chrom = dict()

    def __init__(self):
        self.temp_chrom = {"A":0, "B":0, "C":0, "D":0, "E":0, "F":0, "G":0 }

    def parse_length(self, s):
        length = 1
        divs = s.count('/')
        t = s.split('/')[-1]
        num = 0
        if t != '':
            num = int(t)
        if num < 0 or num > 0 and divs > 1:
            # error
            pass
        else:
            if num == 0:
                # e.g. '///'
                length = (1/2) ** divs
            elif divs == 0:
                # e.g. '12'
                length = num
            else:
                # e.g. '/12'
                length = 1/num
        return length

    def parse_note(self, s, len_mult=1):
        mo = re.match(self.re_note, s)
        group_dict = mo.groupdict()

        pitch_level = self.note_dict[group_dict['pitch']]
        note = group_dict['pitch'].upper()
        acc = group_dict['acc']
        if acc != None:
            if acc == '^':
                pitch_level += 1
                self.temp_chrom[note] = 1
            elif acc == '_':
                pitch_level -= 1
                self.temp_chrom[note] = -1
            elif acc == '^^':
                pitch_level += 2
                self.temp_chrom[note] = 2
            elif acc == '__':
                pitch_level -= 2
                self.temp_chrom[note] = -2
            elif acc == '#' or acc == '♯':
                pitch_level += 1
            elif acc == 'b' or acc == '♭':
                pitch_level -= 1
        else:
            pitch_level += self.temp_chrom[note]
        pitch_level -= 12 * group_dict['ext'].count(',')
        pitch_level += 12 * group_dict['ext'].count('\'')
        pitch_level += 12 * group_dict['ext'].count('`')
        
        return (pitch_level, self.parse_length(group_dict['len'])*len_mult)


    def parse_chord(self, s, len_mult=1):
        notes = []
        len_mo = re.search(r"\/*\d*$", s)
        len = len_mult
        if len_mo is not None:
            len *= self.parse_length(len_mo.group(0))

        for mo in re.finditer(self.re_note, s):
            note = mo.group(0)
            parse_result = self.parse_note(note, len_mult=len)
            if parse_result[0] != None:
                notes.append(parse_result)
        
        min_dur = notes[0][1]
        for n in notes:
            if n[1] < min_dur:
                min_dur = n[1]
        return (min_dur, notes)

    def parse_score(self, score):
        result = []
        cur_time = 0
        measures = score.split("|")

        for m in measures:
            self.temp_chrom = {k: 0 for k in self.temp_chrom}
            for mo in re.finditer(self.regex, m):
                kind = mo.lastgroup
                value = mo.group()
                if kind == "NOTE":
                    note = self.parse_note(value)
                    if note[0] != None:
                        result.append((cur_time, note))
                    # increase by duration
                    cur_time += note[1]
                elif kind == "CHORD":
                    min_dur, notes = self.parse_chord(value)
                    for n in notes:
                        result.append((cur_time, n))
                    # increase by shortest note in the chord
                    cur_time += min_dur
        return result

def gen_wav(score, speed=300, volume=1000):
    def fade_in_out(signal, fade_length=1000):
        ''' Adding Fade-in and Fade-out for each note
        
            signal is a numpy array for y values of a wave
            
            fade_length is the number of values that fading are affecting    
        '''
        fade_in = (1 - np.cos(np.linspace(0, np.pi, fade_length))) * 0.5
        fade_out = np.flip(fade_in)
        
        signal[:fade_length] = np.multiply(fade_in, signal[:fade_length])
        signal[-fade_length:] = np.multiply(fade_out, signal[-fade_length:])
    
    p = Parser()
    result = p.parse_score(score)

    # Calculate time of each note
    beat_len = speed / 1000
    # sample/every second
    framerate = 44100

    length = 0
    for note in result:
        end_time = note[0] + note[1][1]
        if end_time > length:
            length = end_time
    
    middle_C = 440 * (2**(-9/12))
    sine_wave_array = np.zeros((int(np.ceil(length * beat_len * framerate))))
    for note in result:
        beat, (pitch_level, length) = note
        sample_start = int(beat_len*framerate*beat)
        sample_count = int(beat_len*framerate*length)
        x = np.linspace(0, beat_len*length, num = int(beat_len*framerate*length))
        freq = middle_C * (2 ** (pitch_level/12))
        y = np.sin(2 * np.pi * freq * x) * volume
        if y.size > 1000:
            fade_in_out(y)
        else:
            fade_len = y.size // 2
            fade_in_out(y, fade_len)
        sine_wave_array[sample_start:(sample_start+sample_count)] += y
    
    sine_wave = np.ndarray.tolist(sine_wave_array)
    return sine_wave

def save(sine_wave):
    # save wav file
    framerate = 44100
    sample_width = 2
    wf = wave.open("data/play/sine.wav", 'wb')
    wf.setnchannels(1)
    wf.setframerate(framerate)
    wf.setsampwidth(sample_width)
    for i in sine_wave:
        data = struct.pack('<h', int(i))
        wf.writeframesraw(data)
    wf.close()
    
    # Convert wave into silk
    silkcoder.encode('data/play/sine.wav', 'data/play/sine.silk', rate=44100)
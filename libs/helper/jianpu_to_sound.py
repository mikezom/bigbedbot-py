import wave
import numpy as np
import struct
import regex as re
from graiax import silkcoder # Convert wav into silk

# Hardcode note frequency
new_freq_list = [
    0.0, # empty
    123.47, # b1.
    130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94, # lower octave
    261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88, # middle octave
    523.25, 554.37, 587.33, 622.25, 659.25, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77, # higher octave
    1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1975.53, # higher higher octave
    2093.00 # #7`
]

# 解决全音和半音
note_dict = {
    'b1' : 0, '1': 1, '#1': 2,
    'b2' : 2, '2': 3, '#2': 4,
    'b3' : 4, '3': 5, '#3': 6,
    'b4' : 5, '4': 6, '#4': 7,
    'b5' : 7, '5': 8, '#5': 9,
    'b6' : 9, '6': 10, '#6': 11,
    'b7' : 11, '7': 12, '#7': 13,
}

def fade_in_out(signal, fade_length=1000):
    ''' Adding Fade-in and Fade-out for each note
    
        signal is a numpy array for y values of a wave
        
        fade_length is the number of values that fading are affecting    
    '''
    fade_in = (1 - np.cos(np.linspace(0, np.pi, fade_length))) * 0.5
    fade_out = np.flip(fade_in)
    
    signal[:fade_length] = np.multiply(fade_in, signal[:fade_length])
    signal[-fade_length:] = np.multiply(fade_out, signal[-fade_length:])

def add_chord_length(chord):
    # for each note in chord, we extend its length
    for note_list in chord:
        note_list[1] += 1

def match_note(note_list):
    # regex will give us a list like ['#', '6', '.']
    note_to_match = note_list[0] + note_list[1]
    if note_list[2] == '.':
        return note_dict[note_to_match] + 1
    elif note_list[2] == '`':
        return note_dict[note_to_match] + 25
    elif note_list[2] == '``':
        return note_dict[note_to_match] + 37
    else:
        return note_dict[note_to_match] + 13

def number_notation_to_silk(speed, score):
    ''' Converting Chinese number notation to silk file
    '''
    # Split score received by note
    num_array = []
    next_is_note = False
    for i in score:
        if i == ' ':
            num_array.append('0')
        elif i == '-':
            num_array.append('-')
        elif i == '[':
            num_array.append('[')
        elif i == ']':
            num_array.append(']')
        else:
            if re.match('[b#]', i): # is a sign
                next_is_note = True
                num_array.append(i) # Start a new element
            elif re.match('[\d]', i) and next_is_note: # is a number, and the previous char is a sign
                num_array[-1] += i
                next_is_note = False
            elif re.match('[`.]', i): # ` and . have to come with a note
                num_array[-1] += i
            else:
                num_array.append(i) # Start a new element
    
    # Convert note into frequency list indexes
    # list_to_change is a list of chords to play, each chord looks like
    # [[5, 2], [6, 2], ...]
    list_to_change = []
    new_chord = []
    is_chord = False
    for note in num_array:
        note_list = re.split('(\d)', note)
        if note_list[0] == '-':
            add_chord_length(list_to_change[-1])
        elif note_list[0] == ']':
            # end of chord
            is_chord = False
            list_to_change.append(new_chord)
        elif note_list[0] == '[':
            # start of chord
            is_chord = True
            new_chord = []
        elif len(note_list) > 1 and note_list[1] == '0':
            # add an empty chord
            list_to_change.append([[0, 1]])
        else:
            note_to_add = match_note(note_list)
            if not is_chord:
                # chord of single note
                list_to_change.append([[note_to_add, 1]])
            else:
                # inside a chord
                new_chord.append([note_to_add, 1])
    
    # Calculate time of each note
    time_const = speed / 1000
    # sample/every second
    framerate = 44100
    # bytes needed every sample
    sample_width = 2
    volume = 2000
    sine_wave_array = np.array([])
    for chords in list_to_change:
        chord_length = chords[0][1]
        # note_num = len(chords)
        x = np.linspace(0, time_const*chord_length, num = int(time_const*framerate*chord_length))
        y_sum = x
        for note, length in chords:
            y = np.sin(2 * np.pi * new_freq_list[note] * x) * volume
            if y.size > 1000:
                fade_in_out(y)
            else:
                fade_len = y.size // 2
                fade_in_out(y, fade_len)
            y_sum = np.add(y, y_sum)
        # y_sum = y_sum * (1 / note_num)
        sine_wave_array = np.append(sine_wave_array, y_sum)
    sine_wave = np.ndarray.tolist(sine_wave_array)
    
    # save wav file
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
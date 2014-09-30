# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 13:30:56 2014

@author: FL232714

2160p: 3840x2160
1440p: 2560x1440
1080p: 1920x1080
720p: 1280x720
480p: 854x480
360p: 640x360
240p: 426x240

"""

from pylab import *
from moviepy.editor import TextClip, CompositeVideoClip, ImageClip, AudioFileClip
from moviepy.editor import concatenate as concat_clips

def display_audio_clip(audio_clip, sample_freq, title_label):
    """ plots the waveform and the spectrogram of the audio clip"""
    t = arange(audio_clip.shape[0], dtype=float32) / sample_freq
    
    f = figure(1, figsize=(8.54, 4.8))
    clf()
    subplot(211)
    plot(t, audio_clip)
    xlabel("time (s)")
    ylabel('amplitude (a. u.)')
    title(title_label)
    grid(True)
    subplot(212)
    specgram(audio_clip, Fs=sample_freq)
    xlim(0, 1.1)
    ylim(0, 10000)
    xlabel('time (s)')
    ylabel('frequency (Hz)')
    tight_layout()
    savefig('tmp.png', dpi=25)
    

def write_audio_clips_to_disk(variations, sample_freq):
    for p in variations.keys()[:]:
        wavfile.write('sound.wav', sample_freq, variations[p].astype(int16))

if __name__ == '__main__':
    screensize = (854, 480)
    clips = []
    # intro screen
    intro_txt = TextClip("""119 Variations\non a theme by Samsung\n'The whistling ringtone'""",
                         color='white', 
                         font='Baskerville Old Face Normal',
                         kerning=5, 
                         fontsize=35)
    
    intro_txt = intro_txt.set_pos('center').set_duration(5)
    intro_cvc = CompositeVideoClip( [intro_txt],
                            size=screensize, transparent=True)
                            
    clips.append(intro_cvc)
    
    # load sound file
    from scipy.io import wavfile
    sample_freq, whistle = wavfile.read("samsung_ringtone.wav")
    t = arange(whistle.shape[0], dtype=float32) / sample_freq
    
    # segment it
    chunk_times = [0., 0.22, 0.38, 0.5, 0.92, 1.2]
    from scipy.signal import get_window    
    chunks = []
    for start, end in zip(chunk_times[:-1], chunk_times[1:]):
        chunks.append(whistle[(t > start) & (t < end)] * get_window('hamming', t[(t > start) & (t < end)].size))    

    # make the permutations
    from itertools import permutations
    from collections import OrderedDict    
    variations = OrderedDict()
    for p in permutations((0, 1, 2, 3, 4)):
        out = []
        for elem in p:
            if len(out) == 0:
                out = chunks[elem].copy() 
            else:
                out = concatenate((out, chunks[elem].copy()))
        variations[str(p)] = out.copy()
    
    cnt = 0
    for p in variations.keys()[:]:
        cnt += 1
        print cnt, 
        p = str(p)
        # title clip
        title_clip = TextClip(p, color='white', fontsize=30).set_pos('center').set_duration(2)        
        clips.append(CompositeVideoClip([title_clip],
                                        size=screensize))
        # generate output files
        display_audio_clip(variations[p], sample_freq, p)
        wavfile.write('sound.wav', sample_freq, variations[p].astype(int16))
        # load them with MoviePy        
        aud_clip = AudioFileClip('sound.wav', fps=sample_freq)
        im_clip = ImageClip("tmp.png")
        im_clip = im_clip.set_audio(aud_clip)
        im_clip = im_clip.set_duration(aud_clip.duration)
        clips.append(CompositeVideoClip([im_clip],
                                        size=screensize))
    video = concat_clips(clips)
    video.to_videofile("SamsungVariations.avi", codec='mpeg4')
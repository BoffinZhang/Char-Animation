# 将视频文件转换为numpy数组和音频
from moviepy.editor import AudioFileClip

import cv2
import numpy as np

def extract_audio(video_fname, audio_fname):
    audio_clip = AudioFileClip(video_fname)
    audio_clip.write_audiofile(audio_fname)

def extract_char(video_fname, output_fname, size):
    cap = cv2.VideoCapture(video_fname)
    
    res = []
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, size)
        res.append(frame)
    
    np.savez(output_fname, imgs=np.array(res))

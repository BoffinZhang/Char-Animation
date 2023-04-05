# 将视频文件转换为numpy数组和音频
from moviepy.editor import AudioFileClip

import cv2
import numpy as np
from tqdm import tqdm

def extract_audio(video_fname, audio_fname):
    audio_clip = AudioFileClip(video_fname)
    audio_clip.write_audiofile(audio_fname)
    audio_clip.close()

def extract_char(video_fname, output_fname, size):
    cap = cv2.VideoCapture(video_fname)
    
    res = []
    if cap.isOpened():
        frame_rate = cap.get(5)
        frame_num = cap.get(7)

    with tqdm(total=frame_num, desc='Resolving images', leave=True, ncols=100, unit='it', unit_scale=True) as pbar:
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.resize(frame, size)
            res.append(frame)
            pbar.update(1)
    
    np.savez(output_fname, imgs=np.array(res), frame_rate=frame_rate, frame_num=frame_num)
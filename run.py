import os
import sys
import cv2
import ctypes
import numpy as np

from time import sleep, time, strftime, gmtime
from threading import Thread
from playsound import playsound

import data_process
from get_args import get_args



args = get_args()

# 同步刷新率
class FrameSyn():
    def __init__(self, frame_num, frame_rate) -> None:
        self.frame_num = frame_num
        self.frame_rate = frame_rate
        self.stime = time()
        self.frame_time = 1.0 / frame_rate
        self.total_time = self.frame_num * self.frame_time

    def check_render(self, c_frame_num):
        # 用于跳帧，来保证高分辨率下仍然可以同步
        # return: True 表示需要渲染当前帧， False 表示跳过当前帧
        target_time = c_frame_num * self.frame_time
        passed_time = time() - self.stime

        if passed_time - 10*self.frame_time > target_time:
            return False
        return True

    def syn(self, c_frame_num):
        target_time = c_frame_num * self.frame_time
        passed_time = time() - self.stime
        wait_time = target_time - passed_time

        print(f'time:  {strftime("%H:%M:%S", gmtime(passed_time))}/{strftime("%H:%M:%S", gmtime(self.total_time))}')
        print(f'frame: {c_frame_num}/{self.frame_num}, rate: {self.frame_rate:.2f}')
        sleep(max(wait_time, 0))


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
    def __init__(self, x, y) -> None:
        super().__init__()
        self.X = x
        self.Y = y

def gotoXY(x, y):
    STD_OUTPUT_HANDLE= -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    dwCursorPosition = COORD(x, y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(std_out_handle,dwCursorPosition)

# 显示单帧图片
def show_img(img):
    img = img / 255
    rows, cols = img.shape
    gotoXY(0, 0)
    char_screen = ''
    for y in range(rows):
        for x in range(cols):
            index =  (img[y, x] * (len(args.char_set) - 1)).astype(int)
            char_screen += args.char_set[index]
            if args.interval:
                char_screen += ' '
        char_screen += '\n'
    print(char_screen, flush=True)

def play_animation(video_fname):

    os.system('cls')
    cap = cv2.VideoCapture(video_fname)
    
    res = []
    if cap.isOpened():
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_num = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        args.height = int(frame_height * args.width // frame_width)
        frame_size = (args.width, args.height) 
    else:
        print('ERROR: CANNOT OPEN VIDEO')
        exit(1)

    # 更改控制台窗口大小
    if args.interval:
        os.system(f'mode con: cols={frame_size[0] * 2} lines={frame_size[1] + 5}')
    else:
        os.system(f'mode con: cols={frame_size[0]    } lines={frame_size[1] + 5}')

    syn = FrameSyn(frame_num, frame_rate)
    count = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, frame_size)

        if syn.check_render(count):
            show_img(frame)
            syn.syn(count)
            print('video_name:',video_fname)
        count += 1
    
    cap.release()


if __name__=='__main__':

    args.video_fullpath = './data/ctrl.mp4'

    filepath, filename = os.path.split(args.video_fullpath)
    name, suffix = os.path.splitext(filename)
    audio_dir = os.path.join(filepath, 'audio')
    audio_fname = os.path.join(audio_dir, name + '.mp3')


    # 加载数据
    if not os.path.exists(args.video_fullpath):
        print('ERROR: FILE NOT EXIST,', args.video_fullpath)
        exit(1)
    
    if not os.path.exists(audio_fname):
        print('extracting audio...')
        os.makedirs(audio_dir, exist_ok=True)
        data_process.extract_audio(args.video_fullpath, audio_fname)
        print('--finished')
    
    # 反转字符集灰度
    if args.reverse_grayscale:
        args.char_set = args.char_set[::-1]

    playsound(audio_fname, block=False)
    play_animation(args.video_fullpath)
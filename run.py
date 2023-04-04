import ctypes
from time import sleep, time
import numpy as np
import os
from threading import Thread
from playsound import playsound

import data_process

# 画面大小
frame_size = (86, 48)


video_fname = './data/ctrl.mp4'
audio_fname = './data/ctrl.wav'
imgs_fname  = f'./data/ctrl_{frame_size[0]}_{frame_size[1]}.npz' 

char_set = '@##!**.   '
# char_set = '@%#*+=-:. '
# char_set = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^\ '

char_set = char_set[::-1]

# 同步刷新率
class FrameSyn():
    def __init__(self, total, framerate) -> None:
        self.total = total
        self.stime = time()
        self.frametime = 1.0 / framerate

    def syn(self, frame_num):
        target_time = frame_num * self.frametime
        wait_time = target_time - (time() - self.stime)
        print(f'target time: {target_time:.4f}s, frame: {frame_num}')
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
            index =  (img[y, x] * (len(char_set) - 1)).astype(int)
            char_screen += char_set[index] + ' '
        char_screen += '\n'
    print(char_screen, flush=True)

def play_imgs(fname='ctrl.npz'):
    stime = time()
    imgs = np.load(fname)['imgs']

    syn = FrameSyn(len(imgs), 25)
    os.system('cls')

    for i, img in enumerate(imgs):
        show_img(img)
        syn.syn(i)

    print('video time', time() - stime, 's')

if __name__=='__main__':

    # 加载数据
    if not os.path.exists(video_fname):
        print('ERROR: FILE NOT EXIST,', video_fname)
        exit(1)
    
    if not os.path.exists(audio_fname):
        print('extracting audio...')
        data_process.extract_audio(video_fname, audio_fname)
        print('--finished')
    
    if not os.path.exists(imgs_fname):
        print('extracting chars...')
        data_process.extract_char(video_fname, imgs_fname, size=frame_size)
        print('--finished')
    
    # 更改控制台窗口大小
    os.system(f'mode con: cols={frame_size[0] * 2} lines={frame_size[1] + 5}')

    # 定义线程
    t1 = Thread(target=play_imgs, args={imgs_fname})
    t2 = Thread(target=playsound, args={audio_fname})

    # 开始执行
    t1.start()
    t2.start()

    # 等待所有线程执行完毕
    t1.join()  
    t2.join()

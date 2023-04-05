import sys
import argparse
from xmlrpc.client import Boolean

def get_args():
    args = argparse.ArgumentParser(description = 'Char Animation Player')

    # compulsive parameters
    args.add_argument("--video_fullpath", type = str, required=True)
    
    # optional parameters
    # 显示宽度：
    args.add_argument('-w', '--width', type=int, default=288)
    # 灰度对应的字符集
    args.add_argument('-c', '--char_set', type=str, default='  .:-=**!#@')

    args.add_argument('--reverse_grayscale', action='store_true', default=False)
    args.add_argument('--interval', action='store_false', default=True)

    args = args.parse_args()
    return args
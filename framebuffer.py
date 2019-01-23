#!/usr/bin/env python3

import sys
import fcntl
import array

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602


class Framebuffer():
    '''Framebuffer device'''
    def __init__(self):
        self.dev = 0
        self.finfo = 0
        self.vinfo = 0

    def open(self, dev_name):
        try:
            self.dev = open(dev_name, 'r+')
        except FileNotFoundError:
            print("Error: " + dev_name + " not found!")
            sys.exit(-1)

    def get_fb_info(self):
        buf = array.array('h', [0])
        fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, buf, 1)

    def write(self):
        self.dev.seek(0)
        self.dev.write(self.dev)
        self.dev.truncate()

    def close(self):
        self.dev.close()


def main():
    f = Framebuffer()
    f.open('/dev/fb0')
    f.get_fb_info()
    f.close()


if __name__ == '__main__':
    main()
    sys.exit(0)

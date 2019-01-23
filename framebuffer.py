#!/usr/bin/env python3

import sys
import fcntl
import struct

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
        fix_fmt = "<16sL4I3HIL2I2H"
        fb_fix_screen_info = struct.pack(fix_fmt, bytes(0),0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        wtf = fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, fb_fix_screen_info, 1)

        var_fmt = "8I3I3I3I3I16I4I"
        fb_var_screen_info = struct.pack(var_fmt, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        wtf = fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, fb_var_screen_info, 1)

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

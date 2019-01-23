#!/usr/bin/env python3

import sys
import fcntl
import struct
from collections import namedtuple

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602

class Framebuffer():
    '''Framebuffer device'''
    def __init__(self):
        self.dev = 0
        self.finfo = 0
        self.vinfo = namedtuple('vinfo', '''
xres yres
xres_virtual yres_virtual
xoffset yoffset
bits_per_pixel
grayscale
red_offset red_length red_msb_right
green_offset green_length green_msb_right
blue_offset blue_length blue_msb_right
transp_offset transp_length transp_msb_right
nonstd
activate
height
width
accel_flags
pixclock
left_margin
right_margin
upper_margin
lower_margin
hsync_len
vsync_len
sync
vmode
rotate
colorspace
reserved_1 reserved_2 reserved_3 reserved_4
''')

    def open(self, dev_name):
        try:
            self.dev = open(dev_name, 'r+')
        except FileNotFoundError:
            print("Error: " + dev_name + " not found!")
            sys.exit(-1)

    def get_fb_info(self):
        # TODO clean this up and error check
        fix_fmt = "<16sL4I3HIL2I2H"
        fix_buf = struct.pack(fix_fmt, bytes(0),0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        fb_fix_screen_info = fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, fix_buf, True)
        print(struct.unpack(fix_fmt, fb_fix_screen_info))

        var_fmt = "8I3I3I3I3I16I4I"
        var_buf = struct.pack(var_fmt, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                                         0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
        fb_var_screen_info = fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, var_buf, True)
        print(struct.unpack(var_fmt, fb_var_screen_info))
        print(self.vinfo._make(struct.unpack(var_fmt, fb_var_screen_info)))

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

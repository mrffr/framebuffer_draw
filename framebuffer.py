#!/usr/bin/env python3

import sys
import fcntl
import struct
from collections import namedtuple

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602


class Finfo_struct:
    def __init__(self, args):
        self.id = args[1]
        self.smem_start = args[2]
        self.smem_len = args[3]
        self.type = args[4]
        self.type_aux = args[5]
        self.visual = args[6]
        self.xpanstep = args[7]
        self.ypanstep = args[8]
        self.ywrapstep = args[9]
        self.line_length = args[10]
        self.mmio_start = args[11]
        self.mmio_len = args[12]
        self.accel = args[13]
        self.capabilities = args[14]
        self.reserved = args[15:]


class Fb_bitfield:
    def __init__(self, offset, length, msb_right):
        self.offset = offset
        self.length = length
        self.msb_right = msb_right


class Vinfo_struct:
    def __init__(self, args):
        self.xres = args[0]
        self.yres = args[1]
        self.xres_virtual = args[2]
        self.yres_virtual = args[3]
        self.xoffset = args[4]
        self.yoffset = args[5]
        self.bits_per_pixel = args[6]
        self.grayscale = args[7]
        self.red = Fb_bitfield(args[8], args[9], args[10])
        self.green = Fb_bitfield(args[11], args[12], args[13])
        self.blue = Fb_bitfield(args[14], args[15], args[16])
        self.transp = Fb_bitfield(args[17], args[18], args[19])
        self.nonstd = args[20]
        self.activate = args[21]
        self.height = args[22]
        self.width = args[23]
        self.accel_flags = args[24]
        self.pixclock = args[25]
        self.left_margin = args[26]
        self.right_margin = args[27]
        self.upper_margin = args[28]
        self.lower_margin = args[29]
        self.hsync_len = args[30]
        self.vsync_len = args[31]
        self.sync = args[32]
        self.vmode = args[33]
        self.rotate = args[34]
        self.colorspace = args[35]
        self.reserved = args[36:]


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
        # TODO clean this up and error check
        fix_fmt = "<16sL4I3HIL2I2H"
        junk_buf = [bytes(0)] + [0 for i in range(14)]
        fix_buf = struct.pack(fix_fmt, *junk_buf)
        fb_fix_screen_info = fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, fix_buf, True)
        self.finfo = Finfo_struct(struct.unpack_from(fix_fmt, fb_fix_screen_info))
        print(self.finfo.line_length)

        var_fmt = "8I3I3I3I3I16I4I"
        junk_buf = [0 for i in range(40)]
        var_buf = struct.pack(var_fmt, *junk_buf)
        fb_var_screen_info = fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, var_buf, True)
        self.vinfo = Vinfo_struct(struct.unpack_from(var_fmt, fb_var_screen_info))
        print(self.vinfo.xres)

    def test_fill(self):
        pass

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
    f.test_fill()
    f.close()


if __name__ == '__main__':
    main()
    sys.exit(0)

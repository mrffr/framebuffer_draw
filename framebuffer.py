#!/usr/bin/env python3

import sys
import fcntl
import struct
import mmap

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602

KDSETMODE = 0x4B3A
KD_TEXT = 0x00
KD_GRAPHICS = 0x01


class Finfo_struct:
    # TODO return members in order
    def __init__(self, args):
        self.id = args[0]
        self.smem_start = args[1]
        self.smem_len = args[2]
        self.type = args[3]
        self.type_aux = args[4]
        self.visual = args[5]
        self.xpanstep = args[6]
        self.ypanstep = args[7]
        self.ywrapstep = args[8]
        self.line_length = args[9]
        self.mmio_start = args[10]
        self.mmio_len = args[11]
        self.accel = args[12]
        self.capabilities = args[13]
        self.reserved = args[14:]


class Fb_bitfield:
    # TODO return members in order
    def __init__(self, offset, length, msb_right):
        self.offset = offset
        self.length = length
        self.msb_right = msb_right


class Vinfo_struct:
    # TODO return members in order
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
        self.tty = 0
        self.finfo = 0
        self.vinfo = 0
        self.fbp = 0

    def open(self, dev_name):
        try:
            self.dev = open(dev_name, 'r+b')
            self.dev.seek(0)
        except FileNotFoundError:
            print("Error: " + dev_name + " not found!")
            sys.exit(-1)

        try:
            self.tty = open("/dev/tty", 'w')
            fcntl.ioctl(self.tty, KDSETMODE, KD_GRAPHICS)
        except FileNotFoundError:
            print("Error: Can't open /dev/tty!")
            sys.exit(-1)

    def get_fb_info(self):
        # TODO clean this up and error check
        var_fmt = "8I 3I 3I 3I 3I 16I 4I"
        junk_buf = [0 for i in range(40)]
        var_buf = struct.pack(var_fmt, *junk_buf)
        fb_var_screen_info = fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, var_buf, True)
        self.vinfo = Vinfo_struct(struct.unpack_from(var_fmt, fb_var_screen_info))

        fix_fmt = "16s L 4I 3H I L 2I 3H"  # white space is ignored
        junk_buf = [bytes(0)] + [0 for i in range(15)]
        fix_buf = struct.pack(fix_fmt, *junk_buf)
        fb_fix_screen_info = fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, fix_buf, True)
        self.finfo = Finfo_struct(struct.unpack_from(fix_fmt, fb_fix_screen_info))

        self.fbp = mmap.mmap(self.dev.fileno(), self.finfo.smem_len)  # defaults are fine
        self.fbp.seek(0)

    def clear(self):
        self.fbp.seek(0)
        self.fbp.write(bytes(0) * self.finfo.smem_len)

    def colour_pixels(self, offset, length, colour):
        self.fbp.seek(0)
        self.fbp.seek(offset)
        self.fbp.write(colour * length)
        # self.dev.seek(offset)
        # self.dev.write(colour * length)
        # self.dev.truncate(self.size)

    def close(self):
        self.fbp.close()  # munmap
        fcntl.ioctl(self.tty, KDSETMODE, KD_TEXT)
        self.dev.close()
        self.tty.close()

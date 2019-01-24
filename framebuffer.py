#!/usr/bin/env python3

# TODO:
# FBIOPUT_VSCREENINFO
# large assumptions
# die sanely and restore tty

import sys
import fcntl
import struct
import mmap
import ctypes

FBIOGET_VSCREENINFO = 0x4600
FBIOGET_FSCREENINFO = 0x4602

KDSETMODE = 0x4B3A
KD_TEXT = 0x00
KD_GRAPHICS = 0x01


class Finfo_struct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 16),
        ("smem_start", ctypes.c_ulong),
        ("smem_len", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("type_aux", ctypes.c_uint32),
        ("visual", ctypes.c_uint32),
        ("xpanstep", ctypes.c_uint16),
        ("ypanstep", ctypes.c_uint16),
        ("ywrapstep", ctypes.c_uint16),
        ("line_length", ctypes.c_uint32),
        ("mmio_start", ctypes.c_ulong),
        ("mmio_len", ctypes.c_uint32),
        ("accel", ctypes.c_uint32),
        ("capabilities", ctypes.c_uint16),
        ("reserved", ctypes.c_uint16 * 2)
        ]

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
        self.finfo = 0  # fixed screen info
        self.vinfo = 0  # var screen info
        self.fbp = 0  # frame buffer pointer

    def open(self):
        '''Open framebuffer and tty'''
        try:
            self.dev = open("/dev/fb0", 'r+b')
            self.dev.seek(0)
        except FileNotFoundError:
            print("Error: /dev/fb0 not found!")
            sys.exit(-1)

        try:
            # set tty to turn off cursor and blinking
            self.tty = open("/dev/tty", 'w')
            # fcntl.ioctl(self.tty, KDSETMODE, KD_GRAPHICS)
        except FileNotFoundError:
            print("Error: Can't open /dev/tty!")
            sys.exit(-1)

    def get_screen_info(self):
        '''Get fixed and variable screen info'''
        # TODO clean this up and error check
        var_fmt = "8I 3I 3I 3I 3I 16I 4I"
        junk_buf = [0 for i in range(40)]
        var_buf = struct.pack(var_fmt, *junk_buf)
        fb_var_screen_info = fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, var_buf, True)
        self.vinfo = Vinfo_struct(struct.unpack_from(var_fmt, fb_var_screen_info))

        fixed_buf = Finfo_struct()
        if(fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, buf, True) != 0):
            print("Error getting fixed screen info!")
            sys.exit(-1)
        self.finfo = Finfo_struct.from_buffer_copy(fixed_buf)

        # mmap the framebuffer device so fbp points to it
        self.fbp = mmap.mmap(self.dev.fileno(), self.finfo.smem_len)  # defaults are fine
        self.fbp.seek(0)

    def clear(self):
        self.fbp.seek(0)
        self.fbp.write(bytes(0) * self.finfo.smem_len)

    def colour_pixels(self, offset, length, colour):
        self.fbp.seek(0)
        self.fbp.seek(offset)
        self.fbp.write(colour * length)

    def close(self):
        self.fbp.close()  # munmap
        # fcntl.ioctl(self.tty, KDSETMODE, KD_TEXT)
        self.dev.close()
        self.tty.close()

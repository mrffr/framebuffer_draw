#!/usr/bin/env python3

import sys
import fcntl
import mmap
import ctypes

FBIOGET_VSCREENINFO = 0x4600
FBIOPUT_VSCREENINFO = 0x4601
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

class Fb_bitfield(ctypes.Structure):
    _fields_ = [
        ("offset", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("msb_right", ctypes.c_uint32)
        ]


class Vinfo_struct(ctypes.Structure):
    _fields_ = [
        ("xres", ctypes.c_uint32),
        ("yres", ctypes.c_uint32),
        ("xres_virtual", ctypes.c_uint32),
        ("yres_virtual", ctypes.c_uint32),
        ("xoffset", ctypes.c_uint32),
        ("yoffset", ctypes.c_uint32),
        ("bits_per_pixel", ctypes.c_uint32),
        ("grayscale", ctypes.c_uint32),
        ("red", Fb_bitfield),
        ("green", Fb_bitfield),
        ("blue", Fb_bitfield),
        ("transp", Fb_bitfield),
        ("nonstd", ctypes.c_uint32),
        ("activate", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("accel_flags", ctypes.c_uint32),
        ("pixclock", ctypes.c_uint32),
        ("left_margin", ctypes.c_uint32),
        ("right_margin", ctypes.c_uint32),
        ("upper_margin", ctypes.c_uint32),
        ("lower_margin", ctypes.c_uint32),
        ("hsync_len", ctypes.c_uint32),
        ("vsync_len", ctypes.c_uint32),
        ("sync", ctypes.c_uint32),
        ("vmode", ctypes.c_uint32),
        ("rotate", ctypes.c_uint32),
        ("colorspace", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 4)
        ]


class Framebuffer():
    '''Framebuffer device'''
    def __init__(self):
        self.dev = 0
        self.tty = 0
        self.finfo = 0  # fixed screen info
        self.vinfo = 0  # var screen info
        self.orig_vinfo = 0  # original var screen info
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

    def get_finfo(self):
        fixed_buf = Finfo_struct()
        if(fcntl.ioctl(self.dev, FBIOGET_FSCREENINFO, fixed_buf, True) != 0):
            print("Error getting fixed screen info!")
            self._close_fb()
        self.finfo = Finfo_struct.from_buffer_copy(fixed_buf)

    def get_vinfo(self):
        var_buf = Vinfo_struct()
        if(fcntl.ioctl(self.dev, FBIOGET_VSCREENINFO, var_buf, True) != 0):
            print("Error getting variable screen info!")
            self._close_fb()
        self.vinfo = Vinfo_struct.from_buffer_copy(var_buf)
        self.orig_vinfo = Vinfo_struct.from_buffer_copy(var_buf)

    def put_vinfo(self):
        '''change variable info'''
        # TODO: issues with this
        vinfo = bytes(self.vinfo) # serialize ctype struct
        res = fcntl.ioctl(self.dev, FBIOPUT_VSCREENINFO, vinfo, False)
        # print(res == vinfo) # returning the vinfo data
        # print("Error setting variable screen info!")

    def restore_vinfo(self):
        '''call this to "restore" the var info in case it was set'''
        self.vinfo = self.orig_vinfo
        self.put_vinfo()

    def memmap_fb(self):
        '''mmap the framebuffer device so that fbp points to it'''
        # defaults for mmap are fine
        self.fbp = mmap.mmap(self.dev.fileno(), self.finfo.smem_len)
        self.fbp.seek(0)

    def setup(self):
        '''get fixed and variable info and setup memmap for framebuffer'''
        self.get_finfo()
        self.get_vinfo()
        self.memmap_fb()

    def clear(self):
        '''clear the framebuffer'''
        self.fbp.seek(0)
        self.fbp.write(bytes(1) * self.finfo.smem_len) # potential here

    def colour_pixels(self, offset, length, colour):
        # prevent some out of bounds drawing - things will wrap around though
        if offset + length >= self.finfo.smem_len or offset <= 0:
            return
        self.fbp.seek(0)
        self.fbp.seek(offset)
        self.fbp.write(colour * length)

    def _close_fb(self):
        # die and clean up otherwise bad things will happen
        fcntl.ioctl(self.tty, KDSETMODE, KD_TEXT)
        self.dev.close()
        self.tty.close()

    def close(self):
        '''close the framebuffer'''
        self.fbp.close()  # munmap
        self._close_fb()
        

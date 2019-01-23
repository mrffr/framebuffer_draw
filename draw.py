#!/usr/bin/env python3

import framebuffer
import struct
import sys
import time


def pix_colour(r, g, b, vinfo):
    return (r << vinfo.red.offset) | (g << vinfo.green.offset) | (b << vinfo.blue.offset)


def main():
    f = framebuffer.Framebuffer()
    f.open()
    f.get_fb_info()
    # print(f.finfo.__dict__)
    # print(f.vinfo.__dict__)

    f.clear()

    for y in range(f.vinfo.yres):
        location = (y + f.vinfo.yoffset) * f.finfo.line_length
        col = struct.pack('I', pix_colour(y % 255, 255, 255, f.vinfo))
        f.colour_pixels(location, f.vinfo.xres, col)
    time.sleep(1)

    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

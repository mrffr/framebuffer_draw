#!/usr/bin/env python3

import framebuffer
import sys
import struct


def pix_colour(r, g, b, vinfo):
    return (r << vinfo.red.offset) | (g << vinfo.green.offset) | (b << vinfo.blue.offset)


def main():
    f = framebuffer.Framebuffer()
    f.open('/dev/fb0')
    f.get_fb_info()
    print(f.finfo.__dict__)
    print(f.vinfo.__dict__)

    for y in range(f.vinfo.yres):
        for x in range(f.vinfo.xres):
            location = (x + f.vinfo.xoffset) * (f.vinfo.bits_per_pixel//8) + (y + f.vinfo.yoffset) * f.finfo.line_length
            col = struct.pack('I', pix_colour(255, 255, 255, f.vinfo))
            f.colour_pixel(location, col)

    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

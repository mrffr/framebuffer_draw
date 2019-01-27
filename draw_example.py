#!/usr/bin/env python3

import framebuffer
import struct
import sys
import time
import random

# TODO: see if transparency works, probably not

def pix_location(f, x, y):
    return (x + f.vinfo.xoffset) * (f.vinfo.bits_per_pixel // 8) + \
            (y + f.vinfo.yoffset) * f.finfo.line_length

def pix_colour(r, g, b, vinfo):
    return struct.pack('I', 
            (r << vinfo.red.offset) | 
            (g << vinfo.green.offset) | 
            (b << vinfo.blue.offset))

def bounds_check(f, x1, y1):
    return x1 < f.vinfo.xres and y1 < f.vinfo.yres

def draw_line(f, x1, y1, x2, y2, col):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx,sy = 1, 1
    if x1 >= x2: sx = -1
    if y1 >= y2: sy = -1
    err = dx/2
    if dx <= dy: err = -dy/2

    while 1:
        if(not bounds_check(f, x1, y1)): return
        f.colour_pixels(pix_location(f, x1, y1), 1, col)
        if x1 == x2 and y1 == y2: return
        e2 = err
        if e2 > -dx :
            err -= dy
            x1 += sx
        if e2 < dy :
            err += dx
            y1 += sy

def draw_random_lines(f):
    for i in range(30):
        col = pix_colour(random.randint(0, 255), 
                random.randint(0, 255), random.randint(0, 255),
                f.vinfo)
        draw_line(f,
                random.randint(0, f.vinfo.xres),
                random.randint(0, f.vinfo.yres),
                random.randint(0, f.vinfo.xres),
                random.randint(0, f.vinfo.yres),
                col)

def main():
    f = framebuffer.Framebuffer()
    f.open()
    f.setup()
    # print(f.finfo.__dict__)
    # print(f.vinfo.__dict__)
    # f.vinfo.xres = 1920
    # f.vinfo.yres = 1080
    f.vinfo.grayscale = 0
    f.vinfo.bits_per_pixel = 32
    f.put_vinfo()

    f.clear()

    draw_line(f, 0, 0, f.vinfo.xres, f.vinfo.yres, pix_colour(255, 255, 255, f.vinfo))

    #for y in range(f.vinfo.yres):
        #location = (y + f.vinfo.yoffset) * f.finfo.line_length
        #col = struct.pack('I', pix_colour(y % 255, 255, 255, f.vinfo))
        #f.colour_pixels(location, f.vinfo.xres, col)

    draw_random_lines(f)
    time.sleep(1)

    # since I set vinfo better restore it now
    f.restore_vinfo()
    
    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

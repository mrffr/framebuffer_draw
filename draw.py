#!/usr/bin/env python3

import framebuffer
import sys


def main():
    f = framebuffer.Framebuffer()
    f.open('/dev/fb0')
    f.get_fb_info()
    print(f.finfo.__dict__)
    print(f.vinfo.__dict__)
    f.close()


if __name__ == "__main__":
    main()
    sys.exit(0)

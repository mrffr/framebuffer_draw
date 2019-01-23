#!/usr/bin/env python3

import sys


class Framebuffer():
    '''Framebuffer device'''
    def __init__(self):
        self.fb = 0

    def open(self, dev_name):
        try:
            self.fb = open(dev_name, 'r+')
        except FileNotFoundError:
            print("Error: " + dev_name + " not found!")
            sys.exit(-1)

    def close(self):
        self.fb.close()


def main():
    f = Framebuffer()
    f.open('/dev/fb0')
    f.close()


if __name__ == '__main__':
    main()
    sys.exit(0)

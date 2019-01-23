#!/usr/bin/env python3


class Framebuffer():
    def __init__(self):
        self.fb = 0

    def open(self, dev_name):
        self.fb = open(dev_name, 'r+')

    def close(self):
        self.fb.close()


if __name__ == '__main__':
    f = Framebuffer()
    f.open('/dev/fb0')
    f.close()

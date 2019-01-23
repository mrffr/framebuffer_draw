#!/usr/bin/env python3

import unittest
import framebuffer


class TestFramebufferDraw(unittest.TestCase):
    def test_no_framebuffer(self):
        f = framebuffer.Framebuffer()
        with self.assertRaises(SystemExit) as cm:
            f.open('/dev/fb1')
        exc = cm.exception
        self.assertEqual(exc.code, -1)


if __name__ == '__main__':
    unittest.main()

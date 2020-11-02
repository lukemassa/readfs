#!/usr/bin/python3

import unittest
import byte_parser

class TestBlock(unittest.TestCase):

    def test_parse_16(self):
        def one_test(word, expected_value):
            actual_value = byte_parser.parse_16(word)
            self.assertEqual(actual_value, expected_value)
        one_test([0x00, 0x00], 0)
        one_test([0x01, 0x00], 1)
        one_test([0xff, 0x00], 255)
        one_test([0x00, 0x01], 256)

    def test_parse_32(self):
        def one_test(word, expected_value):
            actual_value = byte_parser.parse_32(word)
            self.assertEqual(actual_value, expected_value)

        one_test([0x00, 0x00, 0x00, 0x00], 0)
        one_test([0x01, 0x00, 0x00, 0x00], 1)
        one_test([0x00, 0x01, 0x00, 0x00], 256)
        one_test([0x00, 0x00, 0x01, 0x00], 65536)

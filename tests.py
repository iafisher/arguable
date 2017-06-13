#!/usr/bin/env python3

import unittest
import contextlib
import io
import sys

import arguable


class ParserTests(unittest.TestCase):
    def test_long_option(self):
        args = arguable.parse_args('--verbose', ['--verbose'])
        self.assertEqual(args.verbose, True)


    def test_long_option_syntax(self):
        args = arguable.parse_args('-v[verbose]fo', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        args = arguable.parse_args('-fv[verbose]o', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        args = arguable.parse_args('-fov[verbose]', ['-v', '-f'])
        self.assertEqual(args.verbose, True)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)

        with self.assertRaises(SyntaxError):
            # forgot the ending ']'
            arguable.make_parser('-fov[verbose')

        # with repeated options
        args = arguable.parse_args('-fvv[verbose]o', ['-vvvv', '-f'])
        self.assertEqual(args.verbose, 4)
        self.assertEqual(args.f, True)
        self.assertEqual(args.o, False)


    def test_repeatable(self):
        parser = arguable.make_parser('-vv')
        args = parser.parse_args([])
        self.assertEqual(args.v, 0)

        args = parser.parse_args(['-v'])
        self.assertEqual(args.v, 1)

        args = parser.parse_args(['-vvvvv'])
        self.assertEqual(args.v, 5)


    def test_gathering(self):
        parser = arguable.make_parser('-v x y...')
        args = parser.parse_args(['foo', 'bar', 'baz', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, ['bar', 'baz'])
        self.assertEqual(args.v, True)
        with suppress_stderr():
            with self.assertRaises(SystemExit):
                # y requires at least one argument
                parser.parse_args(['1'])

        parser = arguable.make_parser('-v x y...?')
        args = parser.parse_args(['foo', 'bar', 'baz', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, ['bar', 'baz'])
        self.assertEqual(args.v, True)
        # not supplying any arguments for y is just fine
        args = parser.parse_args(['foo', '-v'])
        self.assertEqual(args.x, 'foo')
        self.assertEqual(args.y, [])
        self.assertEqual(args.v, True)


    def test_full(self):
        parser = arguable.make_parser('-vv[verbosity] infile outfile?')
        args = parser.parse_args(['test.xml'])
        self.assertEqual(args.verbosity, 0)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

        args = parser.parse_args(['test.xml', '-v'])
        self.assertEqual(args.verbosity, 1)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, None)

        args = parser.parse_args(['-vv', 'test.xml', 'out.html'])
        self.assertEqual(args.verbosity, 2)
        self.assertEqual(args.infile, 'test.xml')
        self.assertEqual(args.outfile, 'out.html')


@contextlib.contextmanager
def suppress_stderr():
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    yield
    sys.stderr = old_stderr


if __name__ == '__main__':
    unittest.main()

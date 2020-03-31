import math
import unittest

import calc


class TestCalc(unittest.TestCase):

    def setUp(self) -> None:
        self.calc = calc.Calculator()

    def test_operators(self):
        tests = [(2, '1+1'),
                 (3, '1+1+1'),
                 (0, '1-1'),
                 (-1, '1-1-1'),
                 (-1, '-1'),  # unary negation
                 (1, '--1'),
                 (4, '--1--1--1--1'),
                 (10, '------------10'),
                 (7, '1+2*3'),  # order of operations
                 (7, '3*2+1'),
                 (27, '3*3*3'),
                 (3, '3*3/3'),
                 (1, '27/3/3/3'),
                 (9, '(1+2)*3'),  # brackets (parentheses?)
                 (42, '42'),
                 (3, '1 + 2'),
                 (3, '  1 + 2'),
                 (3, '  1 + 2   '),
                 (1, '(((((1)))))'),
                 (8, '(1-(2-3))*4'),
                 ]
        for val, line in tests:
            self.assertEqual(val, self.calc.parse(line))

    def test_numbers(self):
        tests = [(.1, '.1'),
                 (.1, '0.1'),
                 (.1, '000.1'),
                 (.2, '.1+.1'),
                 (.01, '.1*.1'),
                 (1, '.1/.1'),
                 ]
        for val, line in tests:
            self.assertAlmostEqual(val, self.calc.parse(line))

    def test_errors(self):
        tests = ['abc',
                 '(42a',
                 '1+a',
                 '1a',
                 '(1',
                 '']
        for line in tests:
            self.assertRaises(SyntaxError, lambda: self.calc.parse(line))

    def test_divzero(self):
        self.assertTrue(math.isnan(self.calc.parse('1/0')))

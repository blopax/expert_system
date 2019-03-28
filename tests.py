import unittest
import os
import sys

import solver
from parser import Parser


class ListStream:
    def __init__(self):
        self.data = []

    def write(self, s):
        self.data.append(s)

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        sys.stdout = sys.__stdout__


class TestExpertSystem(unittest.TestCase):
    def test_and(self):
        path = 'tests/input/and'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_and_conclusion(self):
        path = 'tests/input/and_conclusion'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_conclusion_same_fact(self):
        path = 'tests/input/conclusion_same_fact'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_eval(self):
        path = 'tests/input/eval'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_imply(self):
        path = 'tests/input/imply'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_not(self):
        path = 'tests/input/not'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_priority(self):
        path = 'tests/input/priority'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_or(self):
        path = 'tests/input/or'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            # print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_xor(self):
        path = 'tests/input/xor'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            print(filename)
            self.assertEqual(solver.treat_entry('{}/{}'.format(path, filename)), out)

    def test_parsing_error(self):
        path = 'tests/input/parsing_error'
        file_list = os.listdir(path)

        for filename in file_list + ['error_31_file_not_found.txt']:
            # print(filename)
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                expected_out = fd.read()
            with ListStream() as print_list:
                Parser('{}/{}'.format(path, filename)).parse_file()
                out = "".join(print_list.data)
            self.assertEqual(out, expected_out)


if __name__ == "__main__":
    unittest.main()

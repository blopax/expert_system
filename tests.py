import unittest
import os

from srcs import expert_system

class TestExpertSystem(unittest.TestCase):
    def test_and(self):
        path = 'tests/input/and'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            self.assertEqual(expert_system.treat_entry('{}/{}'.format(path, filename)), out)

    def test_or(self):
        path = 'tests/input/or'
        file_list = os.listdir(path)
        for filename in file_list:
            with open('tests/output/out_{}'.format(filename), 'r') as fd:
                out = fd.read()
            self.assertEqual(expert_system.treat_entry('{}/{}'.format(path, filename)), out)


# pb quand contradictory le mettre en str et return ds expert system




if __name__ == "__main__":
    unittest.main()

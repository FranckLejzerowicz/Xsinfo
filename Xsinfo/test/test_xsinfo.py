# ----------------------------------------------------------------------------
# Copyright (c) 2022, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pkg_resources
from Xsinfo.xsinfo import run_xsinfo

ROOT = pkg_resources.resource_filename("Xpbs", "test")


class TestXsinfo(unittest.TestCase):

    def setUp(self):

        # first tests files
        self.sinfo = [
            ['c1-1', 'normal*', 'mixed', '47.41', '30/10/0/40', '2', '20', '2',
             '182784', '148683'],
            ['c1-1', 'optimist', 'mixed', '47.41', '30/10/0/40', '2', '20', '2',
             '182784', '148683'],
            ['c1-2', 'optimist', 'allocated', '19.33', '40/0/0/40', '2', '20',
             '2', '182784', '161744'],
            ['c1-2', 'normal*', 'allocated', '19.33', '40/0/0/40', '2', '20',
             '2', '182784', '161744'],
            ['c1-3', 'optimist', 'mixed', '34.68', '38/2/0/40', '2', '20', '2',
             '182784', '131670'],
            ['c1-3', 'normal*', 'mixed', '34.68', '38/2/0/40', '2', '20', '2',
             '182784', '131670'],
            ['c1-4', 'optimist', 'allocated', '37.33', '40/0/0/40', '2', '20',
             '2', '182784', '163153'],
            ['c1-4', 'normal*', 'allocated', '37.33', '40/0/0/40', '2', '20',
             '2', '182784', '163153'],
            ['c1-5', 'optimist', 'allocated', '39.08', '40/0/0/40', '2', '20',
             '2', '182784', '121947'],
            ['c1-5', 'normal*', 'allocated', '39.08', '40/0/0/40', '2', '20',
             '2', '182784', '121947'],
            ['c1-6', 'optimist', 'allocated', '40.73', '40/0/0/40', '2', '20',
             '2', '182784', '148611'],
            ['c1-6', 'normal*', 'allocated', '40.73', '40/0/0/40', '2', '20',
             '2', '182784', '148611'],
            ['c1-7', 'optimist', 'allocated', '30.74', '40/0/0/40', '2', '20',
             '2', '182784', '153733'],
            ['c1-7', 'normal*', 'allocated', '30.74', '40/0/0/40', '2', '20',
             '2', '182784', '153733'],
            ['c1-8', 'optimist', 'mixed', '34.10', '35/5/0/40', '2', '20', '2',
            '182784', '128726'],
            ['c1-8', 'normal*', 'mixed', '34.10', '35/5/0/40', '2', '20', '2',
            '182784', '128726'],
            ['c1-9', 'optimist', 'reserved', '39.60', '40/0/0/40', '2', '20',
             '2', '182784', '158010'],
            ['c1-9', 'normal*', 'reserved', '39.60', '40/0/0/40', '2', '20',
             '2', '182784', '158010'],
            ['c1-10', 'optimist', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132'],
            ['c1-10', 'normal*', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132'],
            ['c2-1', 'optimist', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132'],
            ['c2-1', 'normal*', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132'],
            ['c3-1', 'optimist', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132'],
            ['c3-1', 'normal*', 'idle', '0.01', '0/40/0/40', '2', '20', '2',
            '182784', '184132']]

    def test_xsinfo(self):
        run_xsinfo(True, False)
        with open(self.out_fp) as f_ref:
            self.pbs2_out = f_ref.readlines()
        self.assertEqual(self.pbs2, self.pbs2_out)


if __name__ == '__main__':
    unittest.main()

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
        self.sh1 = '%s/test.sh' % ROOT

        self.pbs1_1_fp = '%s/test_out1.pbs' % ROOT
        self.pbs1_1_out_fp = self.pbs1_1_fp.replace('.pbs', '_test.pbs')
        with open(self.pbs1_1_fp) as f_ref:
            self.pbs1_1 = f_ref.readlines()


    def test_xsinfo(self):
        run_xsinfo(True, False)
        with open(self.out_fp) as f_ref:
            self.pbs2_out = f_ref.readlines()
        self.assertEqual(self.pbs2, self.pbs2_out)


if __name__ == '__main__':
    unittest.main()

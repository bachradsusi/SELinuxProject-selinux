# Authors: Karl MacMillan <kmacmillan@mentalrootkit.com>
#
# Copyright (C) 2006 Red Hat 
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import unittest
import sepolgen.policygen as policygen
import sepolgen.access as access
import sepolgen.refpolicy as refpolicy

class TestPolicyGenerator(unittest.TestCase):
    def setUp(self):
        self.g = policygen.PolicyGenerator()

    def test_av_rules(self):
        av1 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "ioctl"])
        av2 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "open"])
        av3 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "read"])

        avs = access.AccessVectorSet() 
        avs.add_av(av1)
        avs.add_av(av2)
        avs.add_av(av3)

        self.g.add_access(avs)

        self.assertEqual(len(self.g.module.children), 1)
        r = self.g.module.children[0]
        self.assertIsInstance(r, refpolicy.AVRule)
        self.assertEqual(r.to_string(),
            "allow test_src_t test_tgt_t:file { ioctl open read };")

    def test_ext_av_rules(self):
        self.g.set_gen_xperms(True)

        av1 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "ioctl"])
        av1.xperms['ioctl'] = refpolicy.XpermSet()
        av1.xperms['ioctl'].add(42)
        av2 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "ioctl"])
        av2.xperms['ioctl'] = refpolicy.XpermSet()
        av2.xperms['ioctl'].add(1234)
        av3 = access.AccessVector(["test_src_t", "test_tgt_t", "file", "ioctl"])
        av3.xperms['ioctl'] = refpolicy.XpermSet()
        av3.xperms['ioctl'].add(2345)

        avs = access.AccessVectorSet() 
        avs.add_av(av1)
        avs.add_av(av2)
        avs.add_av(av3)

        self.g.add_access(avs)

        self.assertEqual(len(self.g.module.children), 2)

        r1 = self.g.module.children[0]
        self.assertIsInstance(r1, refpolicy.AVRule)
        self.assertEqual(r1.to_string(),
            "allow test_src_t test_tgt_t:file ioctl;")

        r2 = self.g.module.children[1]
        self.assertIsInstance(r2, refpolicy.AVExtRule)
        self.assertEqual(r2.to_string(),
            "allowxperm test_src_t test_tgt_t:file ioctl { 42 1234 2345 };")

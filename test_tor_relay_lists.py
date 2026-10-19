import tempfile, os, unittest, tor_relay_lists as t

CONS = """valid-after 2026-05-01 00:00:00
r a AAAA BBBB 2026-04-30 23:00:00 10.0.0.1 9001 0
a [2001:db8::1]:9001
s Authority Exit Fast Guard HSDir Running Valid
r b AAAA BBBB 2026-04-30 23:00:00 10.0.0.2 9001 0
s Fast Guard Running Valid
r c AAAA BBBB 2026-04-30 23:00:00 10.0.0.2 9002 0
s Fast Running Valid
r d AAAA BBBB 2026-04-30 23:00:00 10.0.0.3 9001 0
r e AAAA BBBB 2026-04-30 23:00:00 10.0.0.3 9002 0
r f AAAA BBBB 2026-04-30 23:00:00 10.0.0.3 9003 0
s Running Valid
"""

class T(unittest.TestCase):
    def setUp(self): self.L = t.build(t.parse(CONS))
    def test_flags(self):
        self.assertEqual(self.L["guards"], {"10.0.0.1", "10.0.0.2"})
        self.assertEqual(self.L["exits-v4"], {"10.0.0.1"})
        self.assertEqual(self.L["authorities-v4"], {"10.0.0.1"})
        self.assertEqual(self.L["exits-v6"], {"2001:db8::1"})
    def test_instances_per_address(self):
        self.assertEqual(self.L["2-or"], {"10.0.0.2"})
        self.assertEqual(self.L["above2-or"], {"10.0.0.3"})
        self.assertEqual(self.L["above1-or"], {"10.0.0.2", "10.0.0.3"})
    def test_file_layout(self):
        with tempfile.TemporaryDirectory() as d:
            t.write(self.L, d, __import__("datetime").datetime(2026, 5, 1))
            lines = open(os.path.join(d, "guards.txt")).read().splitlines()
        self.assertEqual(lines[0], "Updated:"); self.assertTrue(lines[2].startswith("---"))
        self.assertEqual(lines[3:], ["10.0.0.1", "10.0.0.2"])

if __name__ == "__main__": unittest.main()

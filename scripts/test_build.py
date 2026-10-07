import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import build

class RuleBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write("proxy", [])
        self.write("direct", [])
    def write(self, name, rules):
        (self.root / (name + ".json")).write_text(json.dumps({"version": 5, "rules": rules}))
    def test_rejects_every_cross_list_overlap(self):
        for p, d in [
            ({"domain":["a.example.com"]},{"domain":["a.example.com"]}),
            ({"domain":["a.example.com"]},{"domain_suffix":["example.com"]}),
            ({"domain_suffix":["a.example.com"]},{"domain":["a.example.com"]}),
            ({"domain_suffix":["example.com"]},{"domain_suffix":["a.example.com"]}),
        ]:
            self.write("proxy",[p]); self.write("direct",[d])
            with self.assertRaisesRegex(ValueError,"overlap"): build.validate(self.root)
    def test_suffix_boundary_and_empty_lists(self):
        build.validate(self.root)
        self.write("proxy",[{"domain_suffix":["example.com"]}])
        self.write("direct",[{"domain":["notexample.com"]}])
        build.validate(self.root)
    def test_invalid_and_unknown_rules_fail_closed(self):
        for rule in [{"domain":["https://example.com"]},{"domain":["EXAMPLE.COM"]},{"domain":["example.com.."]},{"domain":["例子.测试"]},{"domain":["example.com","example.com"]},{"domain":[42]},{"domain":["example.com"],"ip_cidr":["192.0.2.0/24"]}]:
            self.write("proxy",[rule])
            with self.assertRaises(ValueError): build.validate(self.root)
    def test_second_compile_failure_preserves_both_outputs(self):
        for name in ["proxy","direct"]: (self.root/(name+'.srs')).write_bytes(b'SRS-old')
        def compile(args, **kwargs):
            if args[-1].endswith('direct.json'): raise build.subprocess.CalledProcessError(1,args)
            Path(args[args.index('--output')+1]).write_bytes(b'SRS-new')
        with patch('build.subprocess.run',side_effect=compile):
            with self.assertRaises(build.subprocess.CalledProcessError): build.build('sing-box',self.root)
        for name in ["proxy","direct"]: self.assertEqual((self.root/(name+'.srs')).read_bytes(),b'SRS-old')

if __name__ == '__main__': unittest.main()

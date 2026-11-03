import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

    def test_transitive_header_change_matches_full_scan(self):
        old=scan(self.p)
        (self.p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
        (self.p/'extra.h').write_text('#include "leaf.h"\n')
        (self.p/'leaf.h').write_text('#define LEAF 7\n')
        commit(self.p,'transitive header change')
        incremental=scan(self.p,old)
        full=scan(self.p)
        for key in ['actual','declared','findings']:
            self.assertEqual(incremental[key],full[key])
        self.assertEqual(incremental['actual']['main.o'],['config.h','extra.h','leaf.h','main.c'])
        missing={f['dependency'] for f in incremental['findings'] if f['type']=='MISSING'}
        self.assertEqual(missing,{'config.h','extra.h','leaf.h'})


class Student241880136Tests(unittest.TestCase):
    def test_required_header_deletion_never_reuses_stale_graph(self):
        """Deleting a required header must invalidate the cached graph and fail."""
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'sample'
            fixture(project)
            previous = scan(project)
            self.assertIn('config.h', previous['actual']['main.o'])

            (project / 'config.h').unlink()
            commit(project, 'student: delete required header')

            # GCC -MM must be rerun and reject the missing header. Reusing the
            # stale main.o graph would incorrectly turn this into a success.
            with self.assertRaisesRegex(ValueError, 'COMMAND_FAILED'):
                scan(project, previous)


if __name__=='__main__':unittest.main()

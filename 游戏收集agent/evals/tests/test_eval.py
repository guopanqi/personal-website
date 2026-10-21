import importlib.util
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('game_eval', Path(__file__).parents[1] / 'eval.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / 'evals'
        self.root.mkdir()
        self.patch = patch.multiple(ev, ROOT=self.root, LIBRARY=self.base)
        self.patch.start()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(self.patch.stop)
        self.production = {'taste.txt': b'old taste', '游戏库-Gamer520更新SKILL.md': b'old skill',
                           'game-library.csv': b'unchanged csv', 'gamer520-sync-state.json': b'unchanged cursor',
                           'game-library-doctor-reviews.json': b'unchanged reviews'}
        for name, content in self.production.items():
            (self.base / name).write_bytes(content)
        ev.write(self.base / 'game-library-test-set-draft.json', {
            'status': 'approved_for_benchmark', 'cases': [{'title': 'known', 'result_label': '推荐', 'reason_detail': 'secret'}]})
        ev.write(self.root / 'proposed-cases.json', {'cases': [{
            'id': 'new', 'title': 'new title', 'status': 'pending_review', 'split': 'holdout',
            'expectation': 'secret new answer', 'evidence': [{'text': 'fixed evidence'}]}]})
        (self.root / 'new-taste').write_text('new taste')
        (self.root / 'new-skill').write_text('new skill')

    def prepare(self, split='dev'):
        args = Namespace(name='test', taste=str(self.root / 'new-taste'), skill=str(self.root / 'new-skill'),
                         hypothesis='h', split=split, model='gpt-6-luna', repetition=1)
        ev.prepare(args)
        return self.root / 'experiments/test'

    def output(self):
        return {'model': 'gpt-6-luna', 'results': [{'id': 'legacy-01', 'title': 'known', 'score': 3,
            'result_label': '推荐', **{k: 'specific explanation' for k in ev.FIELDS}}]}

    def import_both(self, folder):
        for variant in ('baseline', 'candidate'):
            raw = folder / variant / 'raw-output.json'
            ev.write(raw, self.output())
            ev.import_output(Namespace(experiment=str(folder), variant=variant, output=str(raw),
                                       agent_id=f'actual-{variant}', bundle=None))

    def test_blind_bundles_and_production_untouched(self):
        folder = self.prepare()
        for variant in ('baseline', 'candidate'):
            bundle = folder / variant
            self.assertEqual(set(p.name for p in bundle.iterdir()), {'inputs.json', 'taste.txt', 'SKILL.md', 'request.md'})
            self.assertNotIn('secret', (bundle / 'inputs.json').read_text())
            self.assertEqual(len(ev.read(bundle / 'inputs.json')), 1)
        self.import_both(folder)
        ev.compare(Namespace(experiment=str(folder)))
        comparison = ev.read(folder / 'comparison.json')
        self.assertEqual(comparison['cases'][0]['verdict'], '不确定')
        for name, content in self.production.items():
            self.assertEqual((self.base / name).read_bytes(), content)

    def test_unreviewed_holdout_is_blocked(self):
        with self.assertRaisesRegex(ValueError, '原有33例'):
            self.prepare('holdout')
        self.assertFalse((self.root / 'experiments/test').exists())

    def test_extensions_stay_disabled_even_if_marked_approved(self):
        path = self.root / 'proposed-cases.json'
        data = ev.read(path)
        data['cases'][0].update(status='approved', split='dev', reviewed_by='user', reviewed_at='2026-10-10')
        ev.write(path, data)
        folder = self.prepare()
        self.assertEqual([c['id'] for c in ev.read(folder / 'inputs.json')], ['legacy-01'])
        self.assertFalse((folder / 'extensions-source.json').exists())

    def test_strength_changes_preserve_recommendation_coverage(self):
        folder = self.prepare()
        self.import_both(folder)
        # Change gold strength, not the model's actual recommendation boundary.
        expected = ev.read(folder / 'expectations.json')
        expected['legacy-01']['result_label'] = '必须推荐'
        ev.write(folder / 'expectations.json', expected)
        manifest = ev.read(folder / 'manifest.json')
        manifest['hashes']['expectations.json'] = ev.digest(folder / 'expectations.json')
        ev.write(folder / 'manifest.json', manifest)
        for variant in ('baseline', 'candidate'):
            path = folder / f'{variant}-result.json'
            run = ev.read(path)
            run['source_manifest_sha256'] = ev.digest(folder / 'manifest.json')
            ev.write(path, run)
        ev.compare(Namespace(experiment=str(folder)))
        comparison = ev.read(folder / 'comparison.json')
        metrics = comparison['metrics']['candidate']
        self.assertEqual(metrics['positive_retained'], 1)
        self.assertEqual(metrics['positive_rejected'], 0)
        self.assertEqual(metrics['recommendation_boundary_matches'], 1)
        self.assertEqual(metrics['exact_label_matches'], 0)
        self.assertEqual(comparison['cases'][0]['candidate_label_assessment'], '推荐强度浮动')
        self.assertEqual(comparison['cases'][0]['verdict'], '不确定')

    def test_label_assessment_separates_misses_strength_and_unknown(self):
        cases = [('必须推荐', '推荐', '推荐强度浮动'),
                 ('推荐', '必须推荐', '推荐强度浮动'),
                 ('必须推荐', '不推荐', '严重漏推荐'),
                 ('推荐', '不推荐', '严重漏推荐'),
                 ('不推荐', '推荐', '误推荐'),
                 ('不推荐', '必须推荐', '误推荐'),
                 ('推荐', '信息不足', '待确认'),
                 ('不推荐', '信息不足', '待确认'),
                 ('不推荐', '不推荐', '一致')]
        for target, predicted, category in cases:
            with self.subTest(target=target, predicted=predicted):
                self.assertEqual(ev.label_assessment(target, predicted), category)

    def test_explicit_diagnostic_excludes_real_games_and_preserves_gold(self):
        path = self.root / 'proposed-cases.json'
        data = ev.read(path)
        data['cases'][0]['evidence'][0]['kind'] = 'synthetic_controlled_fixture'
        data['cases'].append({'id': 'real', 'title': 'Real game', 'evidence': [{'kind': 'gameplay', 'text': 'real'}]})
        ev.write(path, data)
        original = (self.base / 'game-library-test-set-draft.json').read_bytes()
        args = Namespace(name='aux', taste=str(self.root / 'new-taste'), skill=str(self.root / 'new-skill'),
                         hypothesis='h', split='diagnostic', model='gpt-6-luna', repetition=1,
                         diagnostic_cases=str(path))
        ev.prepare(args)
        folder = self.root / 'experiments/aux'
        self.assertEqual([c['id'] for c in ev.read(folder / 'inputs.json')], ['new'])
        self.assertEqual(ev.read(folder / 'manifest.json')['experiment_mode'], 'auxiliary_diagnostic')
        self.assertIsNone(ev.read(folder / 'expectations.json')['new']['result_label'])
        self.assertNotIn('expectation', ev.read(folder / 'baseline/inputs.json')[0])
        self.assertEqual((self.base / 'game-library-test-set-draft.json').read_bytes(), original)

    def test_missing_duplicate_and_invalid_score(self):
        inputs = [{'id': 'legacy-01', 'title': 'known'}]
        for change in ('missing', 'duplicate', 'bool_score', 'inconsistent_unknown'):
            data = self.output()
            if change == 'missing': data['results'] = []
            if change == 'duplicate': data['results'] *= 2
            if change == 'bool_score': data['results'][0]['score'] = True
            if change == 'inconsistent_unknown': data['results'][0]['score'] = None
            with self.subTest(change=change), self.assertRaises(ValueError):
                ev.validate_output(data, inputs, 'gpt-6-luna')

    def test_snapshot_tampering_and_no_overwrite(self):
        folder = self.prepare()
        self.import_both(folder)
        with self.assertRaisesRegex(ValueError, '覆盖'):
            ev.import_output(Namespace(experiment=str(folder), variant='baseline',
                output=str(folder / 'baseline/raw-output.json'), agent_id='a', bundle=None))
        (folder / 'candidate-taste.txt').write_text('tampered')
        with self.assertRaisesRegex(ValueError, '快照被改动'):
            ev.compare(Namespace(experiment=str(folder)))

    def test_import_rejects_changed_runner_inputs(self):
        folder = self.prepare()
        (folder / 'candidate/SKILL.md').write_text('different')
        raw = folder / 'candidate/raw-output.json'
        ev.write(raw, self.output())
        with self.assertRaisesRegex(ValueError, '运行输入'):
            ev.import_output(Namespace(experiment=str(folder), variant='candidate', output=str(raw), agent_id='a', bundle=None))

    def test_compare_rejects_changed_model_results(self):
        folder = self.prepare()
        self.import_both(folder)
        path = folder / 'candidate-result.json'
        data = ev.read(path)
        data['results'][0]['judgment'] = 'rewritten answer'
        ev.write(path, data)
        with self.assertRaisesRegex(ValueError, '导入结果被改动'):
            ev.compare(Namespace(experiment=str(folder)))


if __name__ == '__main__':
    unittest.main()

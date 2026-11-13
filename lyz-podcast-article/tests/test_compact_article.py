import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('compact_article', SCRIPTS / 'compact_article.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class CompactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.source = self.base / 'source.md'
        self.source.write_text('Alice says: simplify the process.\n\nHow did you do it?\n\nI removed an unnecessary step. Then I tested it.', encoding='utf-8')
        self.output = self.base / 'delivery' / '文章.md'
        self.guests = ['Alice']
        result = m.start(self.source, self.output)
        self.work = Path(result['work'])
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(lambda: shutil.rmtree(self.work, ignore_errors=True))

    def load(self):
        return m.load(self.work)[1]

    def save(self, s):
        m.save(self.work, s)

    def intake(self):
        s = self.load()
        for n in range(1, len(s['chunks']) + 1):
            m.read_chunk(self.work, n)
        s = self.load()
        s['intake'] = {'identity': {'guests': self.guests, 'program': None, 'topic': 'simplification',
                          'anchors': [{'field': 'guest', 'value': 'Alice', 'paragraph': 'P00001', 'quote': 'Alice'},
                                      {'field': 'topic', 'value': 'simplification', 'paragraph': 'P00001', 'quote': 'simplify the process'}]},
                       'chunk_notes': [{'chunk': i, 'source_paragraphs': c, 'note': 'Alice removes a step then tests the simplified process.'} for i, c in enumerate(s['chunks'], 1)],
                       'context_comparison': {'status': 'none', 'reason': 'No supplied background; filename checked.'}}
        if 'Bob' in self.guests:
            s['intake']['identity']['anchors'].append({'field': 'guest', 'value': 'Bob', 'paragraph': 'P00001', 'quote': 'Bob'})
        self.save(s)
        self.assertTrue(m.preflight(self.work)['ok'])

    def plan(self):
        self.intake()
        s = self.load()
        s['plan'] = [{'question_text': '怎样做？', 'question': {'paragraph': 'P00002', 'quote': 'How did you do it?'},
                      'answer_paragraphs': ['P00003'], 'answer_anchors': [{'paragraph': 'P00003', 'quote': 'I removed an unnecessary step.'}],
                      'note': 'Keep sequence: remove first, test second. Do not claim automation.'}]
        self.save(s)
        self.assertTrue(m.plan_check(self.work)['ok'])

    def draft(self, text=None):
        self.plan()
        text = text or '# 先简化\n\n## 删除一步\n\n**好奇：怎样做？**\n\n**回答：** 我删掉了一个不必要的步骤。\n\n然后测试了一下。\n'
        (self.work / '文章.md').write_text(text, encoding='utf-8')
        s = self.load()
        s['review'] = {'article_sha256': m.digest(text.encode()), 'reviewer': 'fixture, not model', 'reviewed_at': '2026-11-13',
                       'first_pass': {k: True for k in m.FIRST_PASS},
                       'notes': ['Source question and answer matched; original order and tentative tone preserved.'], 'open_core_issues': []}
        self.save(s)

    def test_one_deliverable_and_cleanup(self):
        self.draft()
        self.assertEqual({'session.json', '文章.md'}, {p.name for p in self.work.iterdir()})
        result = m.finish(self.work)
        self.assertTrue(result['delivery_allowed'])
        self.assertFalse(self.work.exists())
        self.assertEqual(['文章.md'], [p.name for p in self.output.parent.iterdir()])
        self.assertEqual(result['article_sha256'], m.digest(self.output.read_bytes()))
        self.assertTrue(self.source.exists())

    def test_unread_refused(self):
        self.assertFalse(m.preflight(self.work)['ok'])

    def test_conflict_unresolved_refused(self):
        self.intake(); s = self.load()
        s['intake']['context_comparison'] = {'status': 'conflict', 'reason': 'Guest differs'}
        self.save(s)
        self.assertFalse(m.preflight(self.work)['ok'])

    def test_conflict_with_explicit_source_choice(self):
        self.intake(); s = self.load()
        s['intake']['context_comparison'] = {'status': 'conflict', 'reason': 'Guest differs', 'resolution': {'action': 'use_transcript', 'reason': 'Explicitly requested input is coherent.'}}
        self.save(s)
        self.assertTrue(m.preflight(self.work)['ok'])

    def test_forged_question_anchor(self):
        self.plan(); s = self.load(); s['plan'][0]['question']['quote'] = 'Invented question'
        self.save(s)
        self.assertFalse(m.plan_check(self.work)['ok'])

    def test_changed_plan_after_draft_refused(self):
        self.draft(); s = self.load(); s['plan'][0]['note'] += ' changed'
        self.save(s)
        self.assertFalse(m.plan_check(self.work)['ok'])
        self.assertFalse(m.check(self.work)['ok'])

    def test_stale_review_hash(self):
        self.draft()
        with (self.work / '文章.md').open('a') as f: f.write('\n变化。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_duplicate_answer_label(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答：** 删除。\n\n**回答：** 测试。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_old_labels_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**问：怎样做？**\n\n**嘉宾：** 删除。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_existing_output_refused_at_start_and_finish(self):
        self.draft(); self.output.parent.mkdir(); self.output.write_text('old')
        with self.assertRaises(ValueError): m.start(self.source, self.output)
        with self.assertRaises(ValueError): m.finish(self.work)
        self.assertEqual('old', self.output.read_text())
        self.assertTrue(self.work.exists())

    def test_multispeaker_turns_allowed(self):
        self.guests = ['Alice', 'Bob']
        self.source.write_text('Alice and Bob discuss: simplify the process.\n\nHow did you do it?\n\nI removed an unnecessary step. Then I tested it.')
        shutil.rmtree(self.work)
        self.work = Path(m.start(self.source, self.output)['work'])
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答（Alice）：** 删除。\n\n然后测试。\n\n**回答（Bob）：** 我也试过。\n')
        self.assertTrue(m.check(self.work)['ok'])

    def test_same_speaker_repeat_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答（Alice）：** 删除。\n\n**回答（Alice）：** 测试。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_empty_answer_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答：**\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_question_count_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答：** 删除。\n\n**好奇：下一步？**\n\n**回答：** 测试。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_docx_extract(self):
        docx = self.base / 'source.docx'
        with zipfile.ZipFile(docx, 'w') as z:
            z.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>hello docx</w:t></w:r></w:p></w:body></w:document>')
        result = m.start(docx, self.base / 'docx.md')
        other = Path(result['work']); self.addCleanup(lambda: shutil.rmtree(other, ignore_errors=True))
        self.assertIn('hello docx', m.read_chunk(other, 1)['text'])

    def test_source_change_refused(self):
        self.plan(); self.source.write_text('changed')
        self.assertFalse(m.preflight(self.work)['ok'])

    def test_keep_work_explicit(self):
        self.draft(); self.assertTrue(m.finish(self.work, keep_work=True)['work_kept'])
        self.assertTrue(self.work.exists())

    def test_unexpected_work_not_deleted(self):
        self.draft(); (self.work / 'other.txt').write_text('unrelated')
        with self.assertRaises(ValueError): m.finish(self.work)
        self.assertFalse(self.output.exists())
        self.assertTrue((self.work / 'other.txt').exists())

    def test_missing_first_pass_review_refused(self):
        self.draft(); s = self.load(); s['review']['first_pass']['spoken_voice_preserved'] = False; self.save(s)
        self.assertFalse(m.check(self.work)['ok'])


    def test_same_count_replaced_question_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：你会自动化吗？**\n\n**回答：** 删除。\n')
        result = m.check(self.work)
        self.assertFalse(result['ok'])
        self.assertTrue(any('question 1 differs' in x for x in result['errors']))

    def test_question_order_refused(self):
        self.plan(); s = self.load()
        s['plan'].append({'question_text': '然后做什么？', 'question': {'paragraph': 'P00002', 'quote': 'How did you do it?'},
                          'answer_paragraphs': ['P00003'], 'answer_anchors': [{'paragraph': 'P00003', 'quote': 'Then I tested it.'}],
                          'note': 'A second fixture question to validate ordering only.'})
        self.save(s); self.assertTrue(m.plan_check(self.work)['ok'])
        text = '# 标题\n\n## 主题\n\n**好奇：然后做什么？**\n\n**回答：** 测试。\n\n**好奇：怎样做？**\n\n**回答：** 删除。\n'
        (self.work / '文章.md').write_text(text)
        s = self.load(); s['review'] = {'article_sha256': m.digest(text.encode()), 'reviewer': 'fixture', 'reviewed_at': '2026-11-13',
                                       'first_pass': {k: True for k in m.FIRST_PASS}, 'notes': ['Fixture only'], 'open_core_issues': []}
        self.save(s)
        result = m.check(self.work)
        self.assertFalse(result['ok'])
        self.assertTrue(any('question 1 differs' in x for x in result['errors']))
        self.assertTrue(any('question 2 differs' in x for x in result['errors']))

    def test_missing_question_text_refused(self):
        self.plan(); s = self.load(); del s['plan'][0]['question_text']; self.save(s)
        self.assertFalse(m.plan_check(self.work)['ok'])


    def test_unknown_speaker_refused(self):
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答（Mallory）：** 删除。\n')
        result = m.check(self.work)
        self.assertFalse(result['ok'])
        self.assertTrue(any('speaker is not grounded' in x for x in result['errors']))

    def test_multispeaker_first_answer_must_identify_speaker(self):
        self.guests = ['Alice', 'Bob']
        self.source.write_text('Alice and Bob discuss: simplify the process.\n\nHow did you do it?\n\nI removed an unnecessary step. Then I tested it.')
        shutil.rmtree(self.work)
        self.work = Path(m.start(self.source, self.output)['work'])
        self.draft('# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答：** 删除。\n\n**回答（Bob）：** 测试。\n')
        self.assertFalse(m.check(self.work)['ok'])

    def test_neutral_speaker_needs_source_anchor(self):
        self.plan(); s = self.load()
        s['intake']['identity']['neutral_speakers'] = [{'label': '受访者B', 'reason': 'A second voice is present.', 'paragraphs': ['P00003'], 'anchors': [{'paragraph': 'P00003', 'quote': 'nonexistent'}]}]
        self.save(s)
        self.assertFalse(m.preflight(self.work)['ok'])

    def test_grounded_neutral_speaker_allowed(self):
        self.plan(); s = self.load()
        s['intake']['identity']['neutral_speakers'] = [{'label': '受访者B', 'reason': 'Fixture only: this source paragraph is the second speaker turn.', 'paragraphs': ['P00003'], 'anchors': [{'paragraph': 'P00003', 'quote': 'Then I tested it.'}]}]
        self.save(s); self.assertTrue(m.preflight(self.work)['ok']); self.assertTrue(m.plan_check(self.work)['ok'])
        text = '# 标题\n\n## 主题\n\n**好奇：怎样做？**\n\n**回答（Alice）：** 删除。\n\n**回答（受访者B）：** 测试。\n'
        (self.work / '文章.md').write_text(text)
        s = self.load(); s['review'] = {'article_sha256': m.digest(text.encode()), 'reviewer': 'fixture', 'reviewed_at': '2026-11-13', 'first_pass': {k: True for k in m.FIRST_PASS}, 'notes': ['Fixture only'], 'open_core_issues': []}
        self.save(s); self.assertTrue(m.check(self.work)['ok'])


if __name__ == '__main__': unittest.main()

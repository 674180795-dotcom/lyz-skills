import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('article_tools',Path(__file__).resolve().parents[1]/'scripts/article_tools.py')
tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.src=self.root/'原文.md';self.src.write_text('嘉宾：可能在明年达到90%，不是现在。\n\n问：什么条件？\n\n嘉宾：需要量产成功。')
        self.work=self.root/'work';tools.prepare(str(self.src),self.work)
        (self.work/'文章_待核稿.md').write_text('# 条件与时间\n\n导语。\n\n## 何时达成\n\n**问：什么条件？**\n\n**嘉宾：** 可能在明年，前提是量产成功。')
    def tearDown(self):self.tmp.cleanup()
    def complete(self):
        p=self.work/'evidence.json';e=json.loads(p.read_text())
        meta=json.loads((self.work/'input.json').read_text())
        e['intake']['identity'].update(topic='量产前提',neutral_guest_reason='原文只标嘉宾，无真实姓名',
            anchors=[{'field':'topic','value':'量产前提','paragraph':'P00003','quote':'需要量产成功'}])
        e['intake']['context_comparison']={'status':'none','reason':'没有额外背景描述'}
        e['intake']['chunk_notes']=[]
        for n,chunk in enumerate(meta['chunks'],1):
            tools.read_chunk(self.work,n)
            e['intake']['chunk_notes'].append({'chunk':n,'source_paragraphs':[chunk[0]],'note':'条件预测，量产是前提；结构测试夹具'})
        e['claims']=[{'id':'C1','text':'有前提的未来预期','article_paragraph':5,'core':True,'status':'attributed','source_ids':['S1'],'source_paragraphs':['P00001','P00003'],'decision':'保留可能和前提','rationale':'字幕只给出有条件的预测'}]
        e['coverage']=[{'article_paragraph':i,'source_paragraphs':['P00001','P00003'],'source_ids':['S1'],'kind':'transcript','note':'单元测试的结构夹具','support':[{'paragraph':'P00003','quote':'需要量产成功'}]} for i in range(1,6)]
        e['speakers']=[{'label':'嘉宾','identity':None,'source_paragraphs':['P00001'],'source_ids':['S1'],'status':'neutral','support':[{'paragraph':'P00001','quote':'嘉宾'}]}]
        e['semantic_review']={'complete':True,'reviewer':'unit-test fixture, not real approval','reviewed_at':'2026-11-01','fact_gate':'pass','notes':['synthetic validation fixture']}
        e['quality']={'scores':dict.fromkeys(tools.DIMENSIONS,18),'reviewer':'synthetic fixture','reviewed_at':'2026-11-01','notes':['not model quality evidence']}
        sha=tools.digest((self.work/'文章_待核稿.md').read_bytes())
        e['semantic_review']['article_sha256']=sha;e['quality']['article_sha256']=sha
        tools.dump(p,e);self.assertTrue(tools.preflight(self.work)['ok']);return e
    def test_fresh_work_and_input_immutable(self):
        before=self.src.read_bytes()
        with self.assertRaises(ValueError):tools.prepare(str(self.src),self.work)
        self.assertEqual(before,self.src.read_bytes())
        self.assertEqual(before,(self.work/'source.bin').read_bytes())
    def test_incomplete_never_promotes(self):
        result=tools.finalize(self.work)
        self.assertFalse(result['ready']);self.assertTrue((self.work/'文章_待核稿.md').exists())
        self.assertIn('semantic fact review incomplete or not passed',result['errors'])
    def test_core_conflict_blocks_even_when_review_says_pass(self):
        e=self.complete();e['claims'][0]['status']='conflict';tools.dump(self.work/'evidence.json',e)
        self.assertFalse(tools.validate(self.work)['ready'])
    def test_missing_mapping_and_invented_refs_block(self):
        e=self.complete();e['coverage'].pop();e['claims'][0]['source_paragraphs']=['P99999'];tools.dump(self.work/'evidence.json',e)
        errors=tools.validate(self.work)['errors']
        self.assertTrue(any('unknown source paragraph' in x for x in errors));self.assertTrue(any('unmapped' in x for x in errors))
    def test_snapshot_and_index_tamper_blocks(self):
        self.complete();(self.work/'paragraphs.json').write_text('[]')
        self.assertFalse(tools.validate(self.work)['ready'])
    def test_only_complete_structural_record_promotes(self):
        self.complete();r=tools.finalize(self.work)
        self.assertTrue(r['ready']);self.assertTrue((self.work/'文章.md').exists())
        self.assertIn('Structural checks',r['warnings'][-1])
    def test_unknown_external_and_bool_score_block(self):
        e=self.complete();e['claims'][0]['source_ids']=['invented'];e['quality']['scores'][tools.DIMENSIONS[0]]=True
        tools.dump(self.work/'evidence.json',e);self.assertFalse(tools.validate(self.work)['ready'])
    def test_symlink_rejected(self):
        (self.work/'source.bin').unlink();(self.work/'source.bin').symlink_to(self.src)
        with self.assertRaises(ValueError):tools.validate(self.work)

    def test_docx_main_body_and_tables_with_misleading_filename(self):
        src=self.root/'Nikita Bier.docx'
        xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Farza Majeed</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>HeyClicky：每天发布产品视频</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
        with zipfile.ZipFile(src,'w') as z:z.writestr('word/document.xml',xml)
        work=self.root/'docx';tools.prepare(str(src),work,context={'title':'Nikita Bier playbook'})
        self.assertEqual((work/'source.bin').read_bytes(),src.read_bytes())
        self.assertIn('Farza Majeed',(work/'source.txt').read_text())
        self.assertIn('HeyClicky',tools.read_chunk(work,1)['text'])
        self.assertFalse(tools.preflight(work)['ok'])
        e=json.loads((work/'evidence.json').read_text())
        e['intake']['identity'].update(guests=['Farza Majeed'],topic='产品视频',anchors=[
            {'field':'guest','value':'Farza Majeed','paragraph':'P00001','quote':'Farza Majeed'},
            {'field':'topic','value':'产品视频','paragraph':'P00002','quote':'每天发布产品视频'}])
        e['intake']['chunk_notes']=[{'chunk':1,'source_paragraphs':['P00001','P00002'],'note':'正文为Farza/HeyClicky产品视频，与标题冲突'}]
        e['intake']['context_comparison']={'status':'none','reason':'测试背景不得漏比'}
        tools.dump(work/'evidence.json',e);self.assertFalse(tools.preflight(work)['ok'])
        e['intake']['context_comparison']={'status':'conflict','reason':'标题Nikita，正文Farza',
            'resolution':{'action':'use_transcript','reason':'明确指定文件，标题是背景，以正文继续'}}
        tools.dump(work/'evidence.json',e);self.assertTrue(tools.preflight(work)['ok'])

    def test_missing_reading_or_notes_block(self):
        self.complete();(self.work/'reading.json').unlink()
        self.assertTrue(any('reading receipts' in x for x in tools.validate(self.work)['errors']))
        e=self.complete();e['intake']['chunk_notes']=[];tools.dump(self.work/'evidence.json',e)
        self.assertFalse(tools.preflight(self.work)['ok'])

    def test_cross_file_reused_evidence_and_receipts_block(self):
        self.complete();other=self.root/'other';tools.prepare(str(self.src),other)
        for name in ['evidence.json','reading.json','intake-status.json']:
            (other/name).write_bytes((self.work/name).read_bytes())
        errors=tools.preflight(other)['errors']
        self.assertTrue(any('different input' in x or 'another input' in x for x in errors))

    def test_background_conflict_requires_explicit_resolution(self):
        e=self.complete();e['intake']['context_comparison']={'status':'conflict','reason':'标题Nikita，正文是另一嘉宾'}
        tools.dump(self.work/'evidence.json',e);self.assertFalse(tools.preflight(self.work)['ok'])
        e['intake']['context_comparison']['resolution']={'action':'use_transcript','reason':'用户明确指定正文文件，附带标题仅提示，按已读正文处理'}
        tools.dump(self.work/'evidence.json',e);self.assertTrue(tools.preflight(self.work)['ok'])

    def test_web_only_qa_is_rejected_even_with_self_reported_pass(self):
        e=self.complete();e['sources'].append({'id':'WEB','kind':'primary','locator':'https://example.com','title':'背景','accessed_at':'2026-11-02','note':'结构夹具'})
        for row in e['coverage']:
            row.update(kind='external',source_ids=['WEB'],source_paragraphs=[],support=[])
        e['claims'][0].update(source_ids=['WEB'],source_paragraphs=[])
        tools.dump(self.work/'evidence.json',e)
        errors=tools.validate(self.work)['errors']
        self.assertTrue(any('Q&A cannot' in x for x in errors))
        self.assertTrue(any('attributed speech' in x for x in errors))

    def test_fabricated_quote_and_wrong_guest_block(self):
        e=self.complete();e['coverage'][-1]['support'][0]['quote']='TBH / Gas 增长策略'
        e['metadata']['guest']='Nikita Bier';tools.dump(self.work/'evidence.json',e)
        errors=tools.validate(self.work)['errors']
        self.assertTrue(any('support quote' in x for x in errors))
        self.assertTrue(any('guest metadata' in x for x in errors))

    def test_post_humanizer_change_requires_new_review_and_finalize(self):
        self.complete();self.assertTrue(tools.finalize(self.work)['ready'])
        self.assertTrue(tools.delivery_check(self.work)['delivery_allowed'])
        article=self.work/'文章.md';article.write_text(article.read_text().replace('可能在明年','已经达到'))
        result=tools.delivery_check(self.work)
        self.assertFalse(result['delivery_allowed'])
        self.assertTrue(any('current article' in x for x in result['errors']))

    def test_preflight_edit_invalidates_receipt(self):
        e=self.complete();e['intake']['identity']['topic']='被替换的主题';tools.dump(self.work/'evidence.json',e)
        self.assertFalse(tools.validate(self.work)['ready'])

    def test_first_and_last_chunks_do_not_count_as_full_reading(self):
        src=self.root/'long.txt';src.write_text('\n\n'.join('第%d段，实际讨论产品视频。'%i*8 for i in range(8)))
        work=self.root/'long';tools.prepare(str(src),work,chunk_chars=100)
        meta=json.loads((work/'input.json').read_text());self.assertGreater(len(meta['chunks']),2)
        tools.read_chunk(work,1);tools.read_chunk(work,len(meta['chunks']))
        self.assertTrue(any('unread or changed chunk' in x for x in tools.preflight(work)['errors']))

    def test_guest_quote_cannot_silently_replace_actual_name(self):
        e=self.complete();e['intake']['identity'].update(guests=['Nikita Bier'],anchors=[
            {'field':'guest','value':'Nikita Bier','paragraph':'P00001','quote':'嘉宾'},
            {'field':'topic','value':'量产前提','paragraph':'P00003','quote':'需要量产成功'}])
        tools.dump(self.work/'evidence.json',e)
        self.assertTrue(any('source name is absent' in x for x in tools.preflight(self.work)['errors']))


if __name__=='__main__':unittest.main()

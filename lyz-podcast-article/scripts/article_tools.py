#!/usr/bin/env python3
"""Local input preparation, evidence structure checks and honest delivery status.

Python 3.9+ standard library only. Never judges truth, changes original inputs,
fetches URLs, invokes a shell, or publishes content.
"""
import argparse
import datetime
import hashlib
import io
import json
import re
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DIMENSIONS = ['主线与导语', '内容取舍', '结构与问答承接', '人物语气', '语言与排版']
CLAIM_STATUSES = {'verified', 'attributed', 'unresolved', 'conflict', 'omitted'}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def record_hash(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8'))


def extract_text(raw, input_format):
    if input_format != 'docx':
        return raw.decode('utf-8-sig')
    # Read only the main document, including table paragraphs. No extraction,
    # macros, links, images, converters, or external entity resolution.
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        info = archive.getinfo('word/document.xml')
        if info.file_size > 32 * 1024 * 1024:
            raise ValueError('DOCX main document exceeds 32 MiB')
        xml = archive.read(info)
    if re.search(br'<!\s*(?:DOCTYPE|ENTITY)', xml, re.I):
        raise ValueError('DOCX XML declarations are not supported')
    root = ET.fromstring(xml)
    ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    body = root.find(ns + 'body')
    if body is None:
        raise ValueError('DOCX has no document body')
    paras = []
    for para in body.iter(ns + 'p'):
        content = ''.join(node.text or '' if node.tag == ns + 't' else
                          '\t' if node.tag == ns + 'tab' else
                          '\n' if node.tag in {ns + 'br', ns + 'cr'} else ''
                          for node in para.iter())
        if content.strip():
            paras.append(content)
    return '\n\n'.join(paras)


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def blocks(text):
    return [p.strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]


def prepare(input_path, out, chunk_chars=6000, context=None):
    if chunk_chars < 100:
        raise ValueError('chunk-chars must be at least 100')
    if input_path == '-':
        raw = sys.stdin.buffer.read()
        origin = 'stdin'
        input_format = 'txt'
    else:
        p = Path(input_path).resolve()
        if p.suffix.lower() not in {'.md', '.txt', '.docx'}:
            raise ValueError('input must be .md, .txt, .docx or - for stdin')
        raw = p.read_bytes()
        origin = str(p)
        input_format = p.suffix.lower().lstrip('.')
    text = extract_text(raw, input_format)
    if not text.strip():
        raise ValueError('input is empty')
    if context is not None and not isinstance(context, dict):
        raise ValueError('context must be a JSON object of user-supplied background')
    out = Path(out)
    if out.exists() or out.is_symlink():
        raise ValueError('output directory already exists; choose a fresh directory')
    out.mkdir(parents=True)
    (out/'source.bin').write_bytes(raw)
    (out/'source.txt').write_text(text, encoding='utf-8')
    records = [{'id': 'P%05d' % i, 'text': t} for i,t in enumerate(blocks(text), 1)]
    dump(out/'paragraphs.json', records)
    (out/'numbered.md').write_text('\n\n'.join('[%s]\n%s' % (r['id'],r['text']) for r in records)+'\n',encoding='utf-8')
    # Chunk boundaries never split a paragraph. Re-read the previous paragraph for context.
    chunks=[]; current=[]; count=0
    for r in records:
        if current and count+len(r['text']) > chunk_chars:
            chunks.append([x['id'] for x in current])
            current=[current[-1]];count=len(current[0]['text'])
        current.append(r);count+=len(r['text'])
    if current: chunks.append([x['id'] for x in current])
    source={'origin': origin,'sha256': digest(raw), 'encoding': 'utf-8-sig',
            'schema_version': 2, 'input_id': str(uuid.uuid4()), 'format': input_format,
            'text_sha256': digest(text.encode('utf-8')), 'provided_context': context or {},
            'characters':len(text), 'paragraph_count':len(records),'chunks':chunks,
            'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    dump(out/'input.json',source)
    evidence={'status':'draft','metadata': {k:None for k in ['guest','program_url','recorded_at','published_at','transcribed_at','clipped_at']},
       'input_binding': {k:source[k] for k in ['input_id','sha256']},
       'intake': {'identity': {'guests': [], 'program': None, 'topic': None,
                             'anchors': [], 'neutral_guest_reason': None},
                  'chunk_notes': [],
                  'context_comparison': {'status': 'unreviewed', 'reason': None,
                                         'resolution': None}},
       'sources':[{'id':'S1','kind':'transcript','locator':'source.bin','title':'用户提供的转录',
                   'accessed_at':source['created_at'][:10],'published_at':None,'note':'仅为文本证据，未听原音'}],
       'claims':[],'coverage':[],'speakers':[],'open_issues':[],
       'semantic_review':{'complete':False,'reviewer':None,'reviewed_at':None,'fact_gate':'unverified','notes':[]},
       'quality':{'scores':{},'reviewer':None,'reviewed_at':None,'notes':[]},'revision_log':[]}
    dump(out/'evidence.json',evidence)
    (out/'content-map.md').write_text('# 内容地图\n\n先读完全部分块。记录主线、前中后主题、关键案例、反例、限制条件、人物细节、来源P编号及留/并/删的理由。\n\n| 主题 | 来源段 | 说话人/录制批次 | 判断与案例 | 条件与反例 | 取舍及理由 |\n|---|---|---|---|---|---|\n',encoding='utf-8')
    return {'work':str(out.resolve()),'paragraphs':len(records),'chunks':len(chunks),'status':'draft'}


def load_inputs(work):
    root=Path(work).resolve()
    for name in ['input.json','paragraphs.json','source.bin','source.txt','reading.json',
                 'intake-status.json','status.json','evidence.json','文章.md','文章_待核稿.md']:
        if (root/name).is_symlink(): raise ValueError('work artifacts must not be symlinks: '+name)
    meta=json.loads((root/'input.json').read_text(encoding='utf-8'))
    paragraphs=json.loads((root/'paragraphs.json').read_text(encoding='utf-8'))
    evidence=json.loads((root/'evidence.json').read_text(encoding='utf-8'))
    return root,meta,paragraphs,evidence


def load_work(work):
    root,meta,paragraphs,evidence=load_inputs(work)
    articles=[root/n for n in ['文章.md','文章_待核稿.md'] if (root/n).is_file()]
    if len(articles)!=1: raise ValueError('exactly one article file required')
    return root,meta,paragraphs,evidence,articles[0]


def source_errors(root, meta, paragraphs):
    errors = []
    raw = (root/'source.bin').read_bytes()
    if digest(raw) != meta.get('sha256'):
        return ['input snapshot hash changed']
    text = extract_text(raw, meta.get('format', 'txt'))
    expected = [{'id': 'P%05d' % i, 'text': t} for i,t in enumerate(blocks(text), 1)]
    if paragraphs != expected:
        errors.append('paragraphs.json no longer matches source snapshot')
    if meta.get('schema_version') != 2:
        errors.append('legacy work has no source gate; prepare a new work directory')
    if meta.get('text_sha256') != digest(text.encode('utf-8')) or not (root/'source.txt').is_file() or (root/'source.txt').read_text(encoding='utf-8') != text:
        errors.append('normalized text no longer matches source snapshot')
    return errors


def chunk_text(meta, paragraphs, number):
    chunks = meta.get('chunks', [])
    if type(number) != int or not 1 <= number <= len(chunks):
        raise ValueError('chunk must be between 1 and %d' % len(chunks))
    indexed = {p['id']: p['text'] for p in paragraphs}
    return '\n\n'.join('[%s]\n%s' % (pid, indexed[pid]) for pid in chunks[number-1])


def read_chunk(work, number):
    root,meta,paragraphs,e = load_inputs(work)
    errors = source_errors(root, meta, paragraphs)
    if errors:
        raise ValueError('; '.join(errors))
    text = chunk_text(meta, paragraphs, number)
    path = root/'reading.json'
    log = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    binding = {k: meta[k] for k in ['input_id','sha256']}
    if log and log.get('input_binding') != binding:
        raise ValueError('reading log belongs to a different input')
    log.setdefault('input_binding', binding)
    log.setdefault('chunks', {})[str(number)] = digest(text.encode('utf-8'))
    dump(path, log)
    return {'input_id':meta['input_id'], 'chunk':number, 'chunk_count':len(meta['chunks']),
            'text':text, 'notice':'Receipt proves text was emitted, not human/model comprehension. Fill chunk_notes after reading.'}


def support_errors(support, indexed, label):
    if not isinstance(support, list) or not support:
        return [label + ': exact transcript support required']
    errors = []
    for anchor in support:
        if not isinstance(anchor, dict):
            errors.append(label + ': invalid support anchor'); continue
        pid,quote = anchor.get('paragraph'), anchor.get('quote')
        if not isinstance(pid, str) or pid not in indexed or not isinstance(quote, str) or not quote.strip() or quote not in indexed.get(pid, ''):
            errors.append(label + ': support quote is absent from this input')
    return errors


def name_supported(value, anchors, record):
    quotes='\n'.join(x.get('quote','') for x in anchors if isinstance(x,dict) and isinstance(x.get('quote'),str))
    if isinstance(value,str) and value.strip() and value.casefold() in quotes.casefold():
        return True
    variant=record.get('source_name')
    return (isinstance(variant,str) and bool(variant.strip()) and
            variant.casefold() in quotes.casefold() and bool(record.get('normalization_reason')))


def intake_errors(root, meta, paragraphs, e, receipt=True):
    errors = source_errors(root, meta, paragraphs)
    if errors:
        return errors
    binding = {k:meta.get(k) for k in ['input_id','sha256']}
    if e.get('input_binding') != binding or not binding['input_id']:
        errors.append('evidence belongs to a different input')
    indexed = {p['id']:p['text'] for p in paragraphs}
    chunks = meta.get('chunks', [])
    if not chunks or set(pid for c in chunks for pid in c) != set(indexed):
        errors.append('chunk index does not cover this input')
    reading = json.loads((root/'reading.json').read_text(encoding='utf-8')) if (root/'reading.json').exists() else {}
    if reading.get('input_binding') != binding:
        errors.append('full transcript reading receipts missing or from another input')
    for number in range(1, len(chunks)+1):
        if reading.get('chunks', {}).get(str(number)) != digest(chunk_text(meta, paragraphs, number).encode('utf-8')):
            errors.append('unread or changed chunk: %d' % number)
    intake = e.get('intake', {})
    if not isinstance(intake, dict):
        return errors + ['intake must be an object']
    notes = intake.get('chunk_notes', [])
    completed = set()
    if not isinstance(notes, list): notes=[]
    for note in notes:
        if not isinstance(note, dict): continue
        n,ps = note.get('chunk'),note.get('source_paragraphs', [])
        if type(n) != int or not 1 <= n <= len(chunks) or n in completed or not isinstance(ps, list) or not ps or not set(ps).issubset(chunks[n-1]) or not isinstance(note.get('note'), str) or not note['note'].strip():
            errors.append('invalid or duplicate chunk note'); continue
        completed.add(n)
    if completed != set(range(1,len(chunks)+1)):
        errors.append('content notes must cover every emitted chunk')
    identity = intake.get('identity', {})
    if not isinstance(identity, dict): identity={}
    guests = identity.get('guests', [])
    if not isinstance(guests, list) or any(not isinstance(g, str) or not g.strip() for g in guests):
        errors.append('identity guests must be a list of names'); guests=[]
    if not guests and not identity.get('neutral_guest_reason'):
        errors.append('guest identity or reason for neutral labels required')
    if not isinstance(identity.get('topic'), str) or not identity['topic'].strip():
        errors.append('actual transcript topic required')
    anchors = identity.get('anchors', [])
    errors += support_errors(anchors, indexed, 'source identity')
    anchors = [x for x in anchors if isinstance(x, dict)] if isinstance(anchors,list) else []
    for field,value in [('guest', g) for g in guests] + [('topic',identity.get('topic'))] + ([('program',identity['program'])] if identity.get('program') else []):
        matching=[x for x in anchors if x.get('field') == field and x.get('value') == value]
        if not matching:
            errors.append('source identity anchor missing: ' + field)
        elif field in {'guest','program'} and not any(name_supported(value,[x],x) for x in matching):
            errors.append('source name is absent from identity quote: '+field)
    comparison = intake.get('context_comparison', {})
    if not isinstance(comparison, dict): comparison={}
    state = comparison.get('status')
    if state not in {'none','match','conflict'} or not comparison.get('reason'):
        errors.append('source/background comparison unresolved')
    if meta.get('provided_context') and state == 'none':
        errors.append('provided background was not compared with transcript')
    if state == 'conflict':
        resolution = comparison.get('resolution')
        if not isinstance(resolution, dict) or resolution.get('action') not in {'use_transcript','user_confirmed'} or not resolution.get('reason'):
            errors.append('source/background conflict needs a reasoned source choice')
    if receipt:
        saved = json.loads((root/'intake-status.json').read_text(encoding='utf-8')) if (root/'intake-status.json').exists() else {}
        if saved.get('ok') is not True or saved.get('input_binding') != binding or saved.get('intake_sha256') != record_hash(intake) or saved.get('context_sha256') != record_hash(meta.get('provided_context',{})):
            errors.append('run preflight for this input and current intake before drafting')
    return errors


def preflight(work):
    root,meta,paragraphs,e=load_inputs(work)
    errors=intake_errors(root,meta,paragraphs,e,receipt=False)
    result={'ok':not errors,'errors':errors,'input_binding':e.get('input_binding'),
            'intake_sha256':record_hash(e.get('intake')),
            'context_sha256':record_hash(meta.get('provided_context',{})),
            'identity':e.get('intake',{}).get('identity'),
            'comparison':e.get('intake',{}).get('context_comparison')}
    dump(root/'intake-status.json',result)
    return result


def validate(work):
    root,meta,paragraphs,e,article=load_work(work)
    errors=[];warnings=[]
    def fail(msg): errors.append(msg)
    text=article.read_text(encoding='utf-8');parts=blocks(text)
    ids={p['id'] for p in paragraphs}
    errors += intake_errors(root,meta,paragraphs,e)
    indexed={p['id']:p['text'] for p in paragraphs}
    article_sha256=digest(article.read_bytes())
    actual_guests=e.get('intake',{}).get('identity',{}).get('guests',[])
    named_guest=e.get('metadata',{}).get('guest')
    if named_guest != (actual_guests[0] if len(actual_guests)==1 else actual_guests or None):
        fail('article guest metadata differs from source identity')
    if len(re.findall(r'^# [^\n]+',text,re.M))!=1: fail('exactly one H1 title required')
    if not re.search(r'^## \S',text,re.M): fail('theme sections required')
    if not re.search(r'\*\*[^\n]*[：:][^\n]*\*\*',text): fail('attributed Q&A required')
    if re.search(r'!\[|^文[丨|]|^编辑[丨|]|^访谈[丨|]|\[\[|```',text,re.M): fail('clipping debris, unearned byline, images or code fences in article')
    if re.search(r'TODO|TBD|待填写|模板提示',text,re.I): fail('unfinished placeholder')
    if '【待核' in text: fail('article contains unresolved marker')
    if e.get('status') not in {'draft','needs_review','ready'}: fail('invalid evidence status')
    lists=['sources','claims','coverage','speakers','open_issues']
    for field in lists:
        if not isinstance(e.get(field),list) or any(not isinstance(x,dict) for x in e[field]): fail(field+' must be a list of objects')
    if errors and any(not isinstance(e.get(f),list) or any(not isinstance(x,dict) for x in e[f]) for f in lists):
        return {'ok':False,'ready':False,'errors':errors,'warnings':warnings,'article':str(article)}
    sources={}
    for s in e['sources']:
        sid=s.get('id')
        if not isinstance(sid,str) or not sid or sid in sources: fail('missing or duplicate source id');continue
        sources[sid]=s
        if s.get('kind') not in {'transcript','primary','secondary','audio'}: fail(sid+': invalid source kind')
        for field in ['locator','title','accessed_at','note']:
            if not isinstance(s.get(field),str) or not s[field].strip(): fail(sid+': missing '+field)
        if s.get('kind') in {'primary','secondary'} and not re.match(r'^https?://',str(s.get('locator',''))): fail(sid+': external source needs URL')
    def refs(item,label):
        ps=item.get('source_paragraphs',[]);ss=item.get('source_ids',[])
        if not isinstance(ps,list) or not isinstance(ss,list): fail(label+': references must be lists');return
        if any(not isinstance(x,str) or x not in ids for x in ps): fail(label+': unknown source paragraph')
        if any(not isinstance(x,str) or x not in sources for x in ss): fail(label+': unknown source id')
        if not ps and not ss: fail(label+': missing evidence reference')
    claim_ids=set()
    if not e['claims']: fail('key claims ledger is empty')
    for c in e['claims']:
        cid=c.get('id')
        if not isinstance(cid,str) or not cid or cid in claim_ids: fail('missing or duplicate claim id');continue
        claim_ids.add(cid);refs(c,cid)
        if not isinstance(c.get('core'),bool): fail(cid+': core must be boolean')
        if c.get('status') not in CLAIM_STATUSES: fail(cid+': invalid claim status')
        if c.get('core') and c.get('status') in {'unresolved','conflict'}: fail(cid+': unresolved core claim')
        ap=c.get('article_paragraph')
        if c.get('status')!='omitted' and (type(ap)!=int or not 1<=ap<=len(parts)): fail(cid+': invalid article paragraph')
        for field in ['text','decision','rationale']:
            if not isinstance(c.get(field),str) or not c[field].strip(): fail(cid+': missing '+field)
        if c.get('status')=='verified' and not c.get('source_ids'): fail(cid+': verified claim needs source id')
        if c.get('status')=='attributed' and not c.get('source_paragraphs'):
            fail(cid+': attributed speech needs transcript paragraphs')
    covered=set()
    for n,c in enumerate(e['coverage'],1):
        label='coverage '+str(n);refs(c,label);ap=c.get('article_paragraph')
        if type(ap)!=int or not 1<=ap<=len(parts): fail(label+': invalid article paragraph')
        else:covered.add(ap)
        if c.get('kind') not in {'transcript','editorial','external'}: fail(label+': invalid kind')
        if c.get('kind')=='external' and not any(sources.get(s,{}).get('kind') in {'primary','secondary'} for s in c.get('source_ids',[])): fail(label+': external paragraph needs external source')
        speech = type(ap)==int and 1<=ap<=len(parts) and bool(re.match(r'^\*\*[^*\n]+[：:]',parts[ap-1]))
        if speech and c.get('kind')!='transcript':
            fail(label+': Q&A cannot be backed by external/editorial content')
        if c.get('kind') in {'transcript','editorial'}:
            if not c.get('source_paragraphs'):
                fail(label+': transcript paragraphs required')
            errors += support_errors(c.get('support'), indexed, label)
            if isinstance(c.get('support'),list) and any(isinstance(x,dict) and x.get('paragraph') not in c.get('source_paragraphs',[]) for x in c['support']):
                fail(label+': quote must belong to mapped transcript paragraphs')
    if covered!=set(range(1,len(parts)+1)): fail('unmapped article paragraphs: '+str(sorted(set(range(1,len(parts)+1))-covered)))
    for s in e['speakers']:
        refs(s,'speaker '+str(s.get('label','?')))
        if s.get('status') not in {'confirmed','neutral','unresolved'}: fail('invalid speaker status')
        if s.get('status')=='unresolved': fail('unresolved speaker attribution')
        if not s.get('source_paragraphs'): fail('speaker needs transcript paragraphs')
        errors += support_errors(s.get('support'),indexed,'speaker '+str(s.get('label','?')))
        if s.get('status')=='confirmed' and not name_supported(s.get('label'),s.get('support',[]) if isinstance(s.get('support'),list) else [],s):
            fail('confirmed speaker name absent from transcript support')
    if not e['speakers']: fail('speaker attribution ledger is empty')
    labels={s.get('label') for s in e['speakers']} | {'问'}
    for part in parts:
        match=re.match(r'^\*\*([^*：:\n]+)[：:]',part)
        if match and match.group(1).strip() not in labels:
            fail('article speech label is absent from source speakers: '+match.group(1).strip())
    for issue in e['open_issues']:
        if not isinstance(issue.get('core'),bool): fail('open issue core must be boolean')
        if issue.get('core'): fail('open core issue: '+str(issue.get('description','?')))
        else:warnings.append('non-core issue: '+str(issue.get('description','?')))
    review=e.get('semantic_review',{})
    if not isinstance(review,dict): review={}
    if review.get('complete') is not True or review.get('fact_gate')!='pass': fail('semantic fact review incomplete or not passed')
    if not review.get('reviewer') or not review.get('reviewed_at') or not review.get('notes'): fail('semantic reviewer evidence missing')
    if review.get('article_sha256')!=article_sha256: fail('semantic review is not bound to current article')
    q=e.get('quality',{});q=q if isinstance(q,dict) else {}
    scores=q.get('scores',{});scores=scores if isinstance(scores,dict) else {}
    if set(scores)!=set(DIMENSIONS) or any(type(v) not in (int,float) or not 16<=v<=20 for v in scores.values()) or sum(scores.values())<90: fail('quality requires five scores >=16 and total >=90')
    if not q.get('reviewer') or not q.get('reviewed_at') or not q.get('notes'): fail('quality review evidence missing')
    if q.get('article_sha256')!=article_sha256: fail('quality review is not bound to current article')
    warnings.append('Structural checks do not verify semantic truth or reviewer identity; inspect cited evidence.')
    return {'ok':not errors,'ready':not errors,'errors':errors,'warnings':warnings,
            'article':str(article),'paragraph_count':len(parts),'claim_count':len(e['claims']),
            'quality_total':sum(v for v in scores.values() if type(v) in (int,float)),
            'input_binding':e.get('input_binding'), 'article_sha256':article_sha256}


def finalize(work):
    verdict=validate(work)
    root,meta,paragraphs,e,article=load_work(work)
    target=root/('文章.md' if verdict['ready'] else '文章_待核稿.md')
    if target!=article:
        if target.exists(): raise ValueError('refusing to overwrite existing article')
        article.rename(target)
    e['status']='ready' if verdict['ready'] else 'needs_review';dump(root/'evidence.json',e)
    editorial=root/'_editorial'
    if editorial.is_symlink(): raise ValueError('_editorial must not be a symlink')
    editorial.mkdir(exist_ok=True)
    report=editorial/'校勘记录.md'
    if report.is_symlink(): raise ValueError('editorial report must not be a symlink')
    lines=['# 校勘记录','', '状态：'+e['status'], '', '原文 SHA256：'+meta['sha256'],'',
           '检查说明：程序仅验证格式、引用索引及审校记录；事实真实性以所列证据和语义审校为准。','',
           '## 素材身份、阅读与背景比对','',json.dumps(e.get('intake',{}),ensure_ascii=False,indent=2),
           '', '## 日期与身份元数据','',json.dumps(e.get('metadata',{}),ensure_ascii=False,indent=2),'','## 校勘与事实','']
    for c in e['claims']:
        lines+=['### '+str(c.get('id','?'))+' · '+str(c.get('status','?')),'',
                str(c.get('text','')),'','原词/原句：'+str(c.get('original','')),'',
                '处理：'+str(c.get('decision','')),'','依据：'+str(c.get('rationale','')),
                '','来源：'+', '.join(c.get('source_ids',[])+c.get('source_paragraphs',[])),'']
    lines+=['## 来源','']
    for s in e['sources']:lines+=['- '+json.dumps(s,ensure_ascii=False)]
    lines+=['','## 说话人判断','',json.dumps(e['speakers'],ensure_ascii=False,indent=2),
            '','## 未决与检查结果','']+['- '+x for x in verdict['errors']+verdict['warnings']]
    lines+=['','## 语义审校与编辑评分','',json.dumps({'semantic_review':e.get('semantic_review'),'quality':e.get('quality'),'revision_log':e.get('revision_log',[])},ensure_ascii=False,indent=2)]
    report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    verdict['article']=str(target);verdict['editorial_record']=str(report);dump(root/'status.json',verdict)
    return verdict


def delivery_check(work):
    verdict=validate(work)
    root,meta,paragraphs,e,article=load_work(work)
    saved=json.loads((root/'status.json').read_text(encoding='utf-8')) if (root/'status.json').exists() else {}
    if saved.get('ready') is not True or saved.get('article_sha256')!=verdict['article_sha256'] or saved.get('input_binding')!=verdict['input_binding'] or saved.get('article')!=str(article):
        verdict['errors'].append('finalize the current article before any downstream delivery')
    verdict['ok']=verdict['ready']=not verdict['errors']
    verdict['delivery_allowed']=verdict['ready']
    return verdict


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('prepare');a.add_argument('--input',required=True);a.add_argument('--out',required=True);a.add_argument('--chunk-chars',type=int,default=6000)
    a.add_argument('--context',help='JSON file with optional user-supplied guest/program/title background')
    a=sub.add_parser('read');a.add_argument('--work',required=True);a.add_argument('--chunk',type=int,required=True)
    for name in ['preflight','check','finalize','delivery-check']:
        a=sub.add_parser(name);a.add_argument('--work',required=True)
    args=p.parse_args()
    try:
        if args.command=='prepare':
            context=json.loads(Path(args.context).read_text(encoding='utf-8')) if args.context else None
            result=prepare(args.input,args.out,args.chunk_chars,context)
        elif args.command=='read': result=read_chunk(args.work,args.chunk)
        elif args.command=='preflight': result=preflight(args.work)
        elif args.command=='check': result=validate(args.work)
        elif args.command=='delivery-check': result=delivery_check(args.work)
        else: result=finalize(args.work)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result.get('ok') is False: return 2
    except (ValueError,OSError,KeyError,TypeError,zipfile.BadZipFile,ET.ParseError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
    return 0


if __name__=='__main__': raise SystemExit(main())

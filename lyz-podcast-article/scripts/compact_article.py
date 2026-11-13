#!/usr/bin/env python3
"""One-file podcast delivery with a temporary, source-bound editing session.

The checks validate records and formatting, never certify comprehension or truth.
Python 3.9+, standard library only. No network, shell, or publishing.
"""
import argparse
import json
import re
import sys
import tempfile
import uuid
from pathlib import Path

from article_tools import blocks, digest, extract_text, name_supported, record_hash, support_errors

SCHEMA = 'podcast-compact-1'
FIRST_PASS = ('questions_grounded', 'meaning_preserved', 'spoken_voice_preserved',
              'no_overediting', 'format_checked')
NOTICE = 'Records prove text output and structural consistency, not comprehension or factual truth.'


def save(root, session):
    (root / 'session.json').write_text(json.dumps(session, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load(work):
    supplied = Path(work)
    if supplied.is_symlink():
        raise ValueError('session directory must not be a symlink')
    root = supplied.resolve()
    for name in ('session.json', '文章.md'):
        if (root / name).is_symlink():
            raise ValueError('session artifacts must not be symlinks')
    s = json.loads((root / 'session.json').read_text(encoding='utf-8'))
    if s.get('schema') != SCHEMA or s.get('work') != str(root) or not s.get('input_id'):
        raise ValueError('invalid or moved editing session')
    return root, s


def source_errors(s):
    try:
        raw = Path(s['origin']).read_bytes()
        if digest(raw) != s.get('sha256'):
            return ['input changed; start a fresh session']
        text = extract_text(raw, s['format'])
        expected = [{'id': 'P%05d' % i, 'text': t} for i, t in enumerate(blocks(text), 1)]
        if expected != s.get('paragraphs'):
            return ['session paragraphs no longer match the original input']
        if make_chunks(expected) != s.get('chunks'):
            return ['session chunk index no longer matches the original input']
    except (OSError, KeyError, ValueError) as exc:
        return ['cannot verify original input: ' + str(exc)]
    return []


def make_chunks(paragraphs):
    chunks, current, size = [], [], 0
    for p in paragraphs:
        if current and size + len(p['text']) > 6000:
            chunks.append([x['id'] for x in current])
            # Overlap a previous paragraph for context, without making a chunk
            # containing only an already-read oversized paragraph.
            current = [current[-1]] if len(current[-1]['text']) < 6000 else []
            size = sum(len(x['text']) for x in current)
        current.append(p)
        size += len(p['text'])
    if current:
        chunks.append([x['id'] for x in current])
    return chunks


def start(input_path, out, context=None):
    origin = Path(input_path).resolve()
    fmt = origin.suffix.lower().lstrip('.')
    if fmt not in ('md', 'txt', 'docx'):
        raise ValueError('input must be md, txt, or docx')
    target = Path(out).expanduser().absolute()
    if target.suffix.lower() != '.md':
        raise ValueError('output must be a Markdown file')
    if target.exists() or target.is_symlink() or target.resolve() == origin:
        raise ValueError('refusing to overwrite an existing file or the input')
    if context is not None and not isinstance(context, dict):
        raise ValueError('context must be a JSON object')
    raw = origin.read_bytes()
    text = extract_text(raw, fmt)
    if not text.strip():
        raise ValueError('input is empty')
    paragraphs = [{'id': 'P%05d' % i, 'text': t} for i, t in enumerate(blocks(text), 1)]
    root = Path(tempfile.mkdtemp(prefix='podcast-article-')).resolve()
    session = {'schema': SCHEMA, 'work': str(root), 'input_id': str(uuid.uuid4()),
               'origin': str(origin), 'sha256': digest(raw), 'format': fmt,
               'output': str(target), 'provided_context': context or {},
               'paragraphs': paragraphs, 'chunks': make_chunks(paragraphs), 'reading': {},
               'intake': {'identity': {'guests': [], 'program': None, 'topic': None,
                                       'anchors': [], 'neutral_guest_reason': None},
                          'chunk_notes': [], 'context_comparison': {'status': 'unreviewed', 'reason': None}},
               'plan': [], 'review': {}}
    save(root, session)
    return {'work': str(root), 'session': str(root / 'session.json'),
            'draft': str(root / '文章.md'), 'output': str(target),
            'chunks': len(session['chunks']), 'notice': NOTICE}


def chunk_text(s, number):
    if type(number) is not int or not 1 <= number <= len(s['chunks']):
        raise ValueError('invalid chunk number')
    indexed = {p['id']: p['text'] for p in s['paragraphs']}
    return '\n\n'.join('[%s]\n%s' % (pid, indexed[pid]) for pid in s['chunks'][number - 1])


def read_chunk(work, number):
    root, s = load(work)
    errors = source_errors(s)
    if errors:
        raise ValueError('; '.join(errors))
    text = chunk_text(s, number)
    s['reading'][str(number)] = digest(text.encode('utf-8'))
    save(root, s)
    return {'chunk': number, 'chunks': len(s['chunks']), 'text': text, 'notice': NOTICE}


def intake_errors(s):
    errors = source_errors(s)
    if errors:
        return errors
    for n in range(1, len(s['chunks']) + 1):
        if s.get('reading', {}).get(str(n)) != digest(chunk_text(s, n).encode('utf-8')):
            errors.append('unread or changed chunk: %d' % n)
    intake = s.get('intake', {})
    indexed = {p['id']: p['text'] for p in s['paragraphs']}
    notes, seen = intake.get('chunk_notes', []), set()
    for note in notes if isinstance(notes, list) else []:
        n = note.get('chunk') if isinstance(note, dict) else None
        if type(n) is not int or not 1 <= n <= len(s['chunks']) or n in seen:
            errors.append('invalid or duplicate chunk note'); continue
        ps = note.get('source_paragraphs', [])
        if not isinstance(ps, list) or not ps or not set(ps).issubset(s['chunks'][n - 1]) or not isinstance(note.get('note'), str) or not note['note'].strip():
            errors.append('each chunk needs specific content notes and source paragraphs')
        seen.add(n)
    if seen != set(range(1, len(s['chunks']) + 1)):
        errors.append('content notes must cover all chunks')
    identity = intake.get('identity', {})
    guests = identity.get('guests', [])
    if not isinstance(guests, list) or any(not isinstance(x, str) or not x.strip() for x in guests):
        errors.append('identity guests must be a list of names'); guests = []
    if not guests and not identity.get('neutral_guest_reason'):
        errors.append('guest identity or neutral label reason is required')
    if not identity.get('topic'):
        errors.append('actual transcript topic is required')
    anchors = identity.get('anchors', [])
    errors += support_errors(anchors, indexed, 'identity')
    valid = anchors if isinstance(anchors, list) else []
    checks = [('guest', x) for x in guests] + [('topic', identity.get('topic'))]
    if identity.get('program'):
        checks.append(('program', identity['program']))
    for field, value in checks:
        matching = [a for a in valid if isinstance(a, dict) and a.get('field') == field and a.get('value') == value]
        if not matching:
            errors.append('identity anchor missing: ' + field)
        elif field != 'topic' and not any(name_supported(value, [a], a) for a in matching):
            errors.append('name absent from transcript identity anchor: ' + field)
    neutral = identity.get('neutral_speakers', [])
    if not isinstance(neutral, list):
        errors.append('neutral_speakers must be a list'); neutral = []
    labels = set(guests)
    for speaker in neutral:
        if not isinstance(speaker, dict):
            errors.append('invalid neutral speaker'); continue
        label = speaker.get('label')
        if not isinstance(label, str) or not label.strip() or label in labels:
            errors.append('neutral speaker labels must be nonempty and distinct')
        else:
            labels.add(label)
        if not speaker.get('reason'):
            errors.append('neutral speaker requires an attribution reason')
        ps = speaker.get('paragraphs', [])
        if not isinstance(ps, list) or not ps or any(pid not in indexed for pid in ps):
            errors.append('neutral speaker requires current-input paragraphs')
        support = speaker.get('anchors', [])
        errors += support_errors(support, indexed, 'neutral speaker')
        if isinstance(support, list) and any(isinstance(a, dict) and a.get('paragraph') not in ps for a in support):
            errors.append('neutral speaker anchor must belong to mapped paragraphs')
    comparison = intake.get('context_comparison', {})
    state = comparison.get('status')
    if state not in ('none', 'match', 'conflict') or not comparison.get('reason'):
        errors.append('source/background comparison unresolved')
    if s.get('provided_context') and state == 'none':
        errors.append('provided background was not compared')
    if state == 'conflict':
        resolution = comparison.get('resolution', {})
        if not isinstance(resolution, dict) or resolution.get('action') not in ('use_transcript', 'user_confirmed') or not resolution.get('reason'):
            errors.append('source/background conflict requires reasoned resolution')
    return errors


def preflight(work):
    root, s = load(work)
    errors = intake_errors(s)
    if not errors:
        s['preflight'] = record_hash(s['intake'])
        save(root, s)
    return {'ok': not errors, 'errors': errors, 'notice': NOTICE}


def plan_errors(s):
    errors = intake_errors(s)
    if s.get('preflight') != record_hash(s.get('intake')):
        errors.append('run preflight for the current intake')
    indexed = {p['id']: p['text'] for p in s['paragraphs']}
    plan = s.get('plan')
    if not isinstance(plan, list) or not plan:
        return errors + ['an ordered source-grounded question/answer plan is required']
    for i, item in enumerate(plan, 1):
        if not isinstance(item, dict):
            errors.append('invalid plan item'); continue
        errors += support_errors([item.get('question')], indexed, 'plan question %d' % i)
        if not isinstance(item.get('question_text'), str) or not item['question_text'].strip():
            errors.append('plan question %d requires final question_text' % i)
        ps = item.get('answer_paragraphs', [])
        if not isinstance(ps, list) or not ps or any(x not in indexed for x in ps):
            errors.append('plan answer sources are required')
        support = item.get('answer_anchors', [])
        errors += support_errors(support, indexed, 'plan answer %d' % i)
        if isinstance(support, list) and any(isinstance(a, dict) and a.get('paragraph') not in ps for a in support):
            errors.append('answer anchor must belong to mapped answer paragraphs')
        if not item.get('note'):
            errors.append('plan must retain meaning, limits, and editorial choice notes')
    return errors


def plan_check(work):
    root, s = load(work)
    errors = plan_errors(s)
    # A plan receipt must exist before prose. A recheck after drafting can only
    # confirm the exact same plan, not retroactively approve a changed one.
    value = record_hash({'intake': s.get('intake'), 'plan': s.get('plan')})
    if (root / '文章.md').exists() and s.get('plan_receipt') != value:
        errors.append('plan must be checked before drafting; changed plans need a fresh draft')
    if not errors:
        s['plan_receipt'] = value
        save(root, s)
    return {'ok': not errors, 'errors': errors, 'notice': NOTICE}


def format_errors(text, plan, identity=None):
    errors, questions, has_answer, last_speaker = [], 0, False, None
    identity = identity or {}
    allowed = set(identity.get('guests', [])) | {s.get('label') for s in identity.get('neutral_speakers', []) if isinstance(s, dict)}
    multiple = len(allowed) > 1
    if len(re.findall(r'^# [^\n]+', text, re.M)) != 1:
        errors.append('exactly one H1 title required')
    if not re.search(r'^## \S', text, re.M):
        errors.append('theme sections required')
    if re.search(r'\*\*(?:问|嘉宾)[：:]', text):
        errors.append('old question/guest labels are not allowed')
    for part in blocks(text):
        qm = re.match(r'^\*\*好奇[：:]([^\n]*?)\*\*$', part)
        am = re.match(r'^\*\*回答(?:（([^）]+)）)?[：:]\*\*\s*(.*)', part, re.S)
        if part.startswith('**好奇') and not qm:
            errors.append('question must be one bold paragraph')
        if qm:
            if questions and not has_answer:
                errors.append('question has no answer')
            if not qm.group(1).strip():
                errors.append('empty question')
            questions += 1; has_answer = False; last_speaker = None
            if questions <= len(plan) and qm.group(1).strip() != plan[questions - 1].get('question_text', '').strip():
                errors.append('article question %d differs from the checked plan question_text or order' % questions)
        elif am:
            speaker = am.group(1) or ''
            if speaker and speaker not in allowed:
                errors.append('answer speaker is not grounded in current-input identity: ' + speaker)
            if multiple and not speaker:
                errors.append('multi-speaker answers must name the grounded speaker at every turn')
            if not questions:
                errors.append('answer appears before a question')
            if not am.group(2).strip():
                errors.append('empty answer')
            if has_answer and (speaker == last_speaker or not speaker or not last_speaker):
                errors.append('repeat answer label in a continuous answer')
            has_answer = True; last_speaker = speaker
        elif part.startswith('**回答'):
            errors.append('invalid answer label')
        elif part.startswith('## ') and questions and not has_answer:
            errors.append('question has no answer before next theme')
    if questions != len(plan):
        errors.append('article questions must match the ordered plan one for one')
    if questions and not has_answer:
        errors.append('last question has no answer')
    if re.search(r'【待核|TODO|TBD|待填写|模板提示', text, re.I):
        errors.append('unresolved marker or placeholder in article')
    return errors


def check(work):
    root, s = load(work)
    errors = plan_errors(s)
    if s.get('plan_receipt') != record_hash({'intake': s.get('intake'), 'plan': s.get('plan')}):
        errors.append('plan or intake changed after plan-check')
    draft = root / '文章.md'
    if not draft.is_file():
        return {'ok': False, 'delivery_allowed': False, 'errors': errors + ['draft is missing']}
    raw = draft.read_bytes(); sha = digest(raw)
    errors += format_errors(raw.decode('utf-8'), s.get('plan', []), s.get('intake', {}).get('identity', {}))
    review = s.get('review', {})
    if review.get('article_sha256') != sha:
        errors.append('review must bind the current article SHA256')
    if not review.get('reviewer') or not review.get('reviewed_at') or not review.get('notes'):
        errors.append('specific semantic review evidence is required')
    if any(review.get('first_pass', {}).get(k) is not True for k in FIRST_PASS):
        errors.append('first-pass meaning, source, voice, and format checks incomplete')
    if review.get('open_core_issues') != []:
        errors.append('core issues must be explicitly closed')
    return {'ok': not errors, 'delivery_allowed': not errors, 'errors': errors,
            'article_sha256': sha, 'draft': str(draft), 'notice': NOTICE}


def finish(work, keep_work=False):
    result = check(work)
    if not result['ok']:
        return result
    root, s = load(work)
    target = Path(s['output'])
    if target.exists() or target.is_symlink() or target.resolve() == Path(s['origin']).resolve():
        raise ValueError('refusing to overwrite the output or original input')
    raw = (root / '文章.md').read_bytes()
    if digest(raw) != result['article_sha256']:
        raise ValueError('draft changed during delivery')
    # Preflight cleanup boundaries before writing any final output.
    removable = (root.name.startswith('podcast-article-') and
                 root.parent == Path(tempfile.gettempdir()).resolve() and
                 {p.name for p in root.iterdir()}.issubset({'session.json', '文章.md'}))
    if not keep_work and not removable:
        raise ValueError('unexpected work directory contents; refusing automatic cleanup')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as f:
        f.write(raw)
    if digest(target.read_bytes()) != result['article_sha256']:
        raise ValueError('delivered bytes failed verification')
    if not keep_work:
        # Exact owned directory only; source files and unrelated temp files are
        # outside this boundary. No recursive wildcard cleanup.
        (root / '文章.md').unlink()
        (root / 'session.json').unlink()
        root.rmdir()
    return {'ok': True, 'delivery_allowed': True, 'article': str(target),
            'article_sha256': result['article_sha256'], 'work_kept': bool(keep_work),
            'notice': NOTICE}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('start'); p.add_argument('--input', required=True); p.add_argument('--out', required=True)
    p.add_argument('--context', help='inline JSON object containing user-supplied background')
    p = sub.add_parser('read'); p.add_argument('--work', required=True); p.add_argument('--chunk', type=int, required=True)
    for command in ('preflight', 'plan-check', 'check', 'finish'):
        p = sub.add_parser(command); p.add_argument('--work', required=True)
        if command == 'finish': p.add_argument('--keep-work', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'start':
            result = start(args.input, args.out, json.loads(args.context) if args.context else None)
        elif args.command == 'read': result = read_chunk(args.work, args.chunk)
        elif args.command == 'preflight': result = preflight(args.work)
        elif args.command == 'plan-check': result = plan_check(args.work)
        elif args.command == 'check': result = check(args.work)
        else: result = finish(args.work, args.keep_work)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result.get('ok') is False else 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

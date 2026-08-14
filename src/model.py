import json, re, unicodedata

items = json.load(open('items.json'))
N = len(items)

CONN = set('│|┃─-—═├┤┬┴┼└┌┐┘╔╗╚╝╠╣╦╩╬┏┓┗┛+▼▲↓↑◄►→←')
VERT = set('│|┃▼▲↓↑')
ARROW_DOWN = set('▼↓')

def txt(i):
    return items[i].get('text', '') if items[i]['k'] == 'p' else None

def is_blank(s):
    return s is None or s.strip() == ''

def conn_ratio(s):
    t = s.strip()
    if not t:
        return 0.0
    c = sum(1 for ch in t if ch in CONN or ch == ' ')
    return c / len(t)

def is_conn_line(s):
    """Line that is purely structural (maybe with a small edge label)."""
    t = s.strip()
    if not t:
        return False
    # pure connector chars
    if all(ch in CONN or ch == ' ' for ch in t):
        return True
    # connector char(s) followed by a short label:  │ dials    |  calls
    m = re.match(r'^[\s]*([│|┃├└┌┼┴┬┤─+▼▲↓↑]+)\s+(.{1,45})$', s)
    if m and not any(ch in CONN for ch in m.group(2).replace('/', '').replace('-', '')):
        return True
    m2 = re.match(r'^[\s]*(.{1,45}?)\s+([│|┃▼▲↓↑]+)\s*$', s)
    if m2 and not any(ch in CONN for ch in m2.group(1)):
        return True
    return False

def has_conn_char(s):
    return any(ch in CONN and ch not in '-+' for ch in s) or bool(re.search(r'\+-{2,}', s)) or bool(re.search(r'-{3,}', s))

SENTENCE_HINT = re.compile(r'\b(the|is|are|this|that|you|we|it|and|of|to|a|in|for|can|be|has|have|its|so|not|but|which|when|what|does|do|will|would|there)\b', re.I)

def is_prose(s):
    t = s.strip()
    if not t:
        return False
    if len(t) > 78:
        return True
    if t.endswith(':'):
        return True
    if t.endswith('.') and len(t.split()) >= 4 and SENTENCE_HINT.search(t):
        return True
    if len(t.split()) >= 9 and SENTENCE_HINT.search(t):
        return True
    return False

def is_nodeish(s):
    """Could be a node label inside a diagram."""
    t = s.strip()
    if not t:
        return False
    if is_prose(t):
        return False
    return len(t) <= 78

# ---------------------------------------------------------------- diagram spans
flag = [False] * N
for i in range(N):
    s = txt(i)
    if s is None:
        continue
    if is_blank(s):
        continue
    if has_conn_char(s) and conn_ratio(s) > 0.30:
        flag[i] = True

def prev_nb(i):
    j = i - 1
    while j >= 0 and items[j]['k'] == 'p' and is_blank(txt(j)):
        j -= 1
    return j

def next_nb(i):
    j = i + 1
    while j < N and items[j]['k'] == 'p' and is_blank(txt(j)):
        j += 1
    return j

# grow: attach node lines adjacent to structural lines
changed = True
while changed:
    changed = False
    for i in range(N):
        if flag[i] or items[i]['k'] != 'p':
            continue
        s = txt(i)
        if is_blank(s) or items[i].get('bold') or items[i].get('list'):
            continue
        if not is_nodeish(s):
            continue
        for j in (prev_nb(i), next_nb(i)):
            if 0 <= j < N and flag[j]:
                flag[i] = True
                changed = True
                break

# spans
spans = []
i = 0
while i < N:
    if flag[i]:
        j = i
        last = i
        while j < N:
            if flag[j]:
                last = j; j += 1
            elif items[j]['k'] == 'p' and is_blank(txt(j)):
                j += 1
            else:
                break
        spans.append((i, last))
        i = last + 1
    else:
        i += 1

span_of = {}
for a, b in spans:
    for k in range(a, b + 1):
        span_of[k] = (a, b)

# ---------------------------------------------------------------- structure
PARTS = [
    dict(no=1, start=0, end=1617,
         title='The Architecture of a Phone Number',
         subtitle='Identifiers, numbering plans and 150 years of switching'),
    dict(no=2, start=1618, end=3237,
         title='Anatomy of a 5G Voice Call',
         subtitle='From pressing CALL to a distributed transaction across a dozen protocols'),
    dict(no=3, start=3238, end=N - 1,
         title='Packet-Level Telecommunications',
         subtitle='SIP, SDP, GTP-U, RTP and the 5G radio stack, field by field'),
]

CHAPTERS = {
 1: [
  ("What a Phone Number Actually Is", 1, 2),
  ("The Global Numbering Plan", 3, 5),
  ("The Identity Family: MSISDN, IMSI, IMEI, ICCID", 6, 10),
  ("The Birth of Automatic Switching", 11, 14),
  ("From Exchanges to National Networks", 15, 18),
  ("Mobility: GSM and the Cellular Model", 19, 22),
  ("Signalling and the Digital PSTN", 23, 25),
  ("The IP Transition: VoIP, SIP and IMS", 26, 29),
  ("Radio, Mobility Management and Paging", 30, 32),
  ("Databases, Authority and International Routing", 33, 35),
  ("Comparisons and Boundary Cases", 36, 39),
  ("Special Numbers and Overlaid Services", 40, 45),
  ("The Whole Evolution in One View", 46, 49),
 ],
 2: [
  ("Setting the Scene", 1, 3),
  ("Attachment: SIM, Cell Search and Registration", 4, 7),
  ("Authentication and the Security Context", 8, 10),
  ("PDU Sessions and IP Connectivity", 11, 12),
  ("IMS Registration", 13, 18),
  ("Placing the Call: the SIP INVITE", 19, 22),
  ("Inter-Operator Routing", 23, 26),
  ("Finding Bob: Paging and Alerting", 27, 31),
  ("Media: Codecs, QoS and RTP", 32, 37),
  ("The 5G Radio Stack", 38, 45),
  ("Generations Compared", 46, 50),
  ("The Entire Call in One Sequence", 51, 51),
  ("Identifiers, Mobility and Roaming", 52, 56),
  ("Protocol Roles and the Deepest Model", 57, 59),
 ],
 3: [
  ("The Packet Stack", 1, 1),
  ("Dissecting a SIP INVITE", 2, 8),
  ("SDP and the Media Description", 9, 11),
  ("From SIP to GTP-U", 12, 16),
  ("Down the Radio Stack", 17, 21),
  ("Where the Phone Number Disappears", 22, 22),
  ("RTP in Detail", 23, 30),
  ("Impairments: Loss, Jitter and RTCP", 31, 34),
  ("Encapsulation, Segmentation and the Control Plane", 35, 40),
  ("Service-Based Architecture and HTTP/2", 41, 42),
  ("Comparing the Layers", 43, 44),
  ("One Packet's Journey", 45, 48),
  ("Reading It in Wireshark", 49, 51),
  ("The Final Mental Model", 52, 52),
 ],
}

SEC_RE = re.compile(r'^(\d+)\.\s+(.*)$')

def build_part(p):
    a, b = p['start'], p['end']
    # find section headings
    secs = []
    for i in range(a, b + 1):
        if items[i]['k'] != 'p':
            continue
        if not items[i].get('bold'):
            continue
        m = SEC_RE.match(items[i]['text'].strip())
        if m:
            secs.append((int(m.group(1)), m.group(2).strip(), i))
    # intro = before first section
    intro_end = secs[0][2] - 1 if secs else b
    out = dict(part=p, intro=(a, intro_end), sections=[])
    for k, (no, title, idx) in enumerate(secs):
        end = secs[k + 1][2] - 1 if k + 1 < len(secs) else b
        out['sections'].append(dict(no=no, title=title, start=idx + 1, end=end))
    return out

parts = [build_part(p) for p in PARTS]

# attach appendix headings (bold non-numbered) found inside sections
def render_range(a, b):
    """Emit list of blocks for item range."""
    blocks = []
    i = a
    while i <= b:
        it = items[i]
        if it['k'] == 'table':
            blocks.append(dict(t='table', rows=it['rows']))
            i += 1
            continue
        s = it['text']
        if is_blank(s):
            i += 1
            continue
        if i in span_of:
            sa, sb = span_of[i]
            sa = max(sa, a); sb = min(sb, b)
            lines = []
            for k in range(sa, sb + 1):
                if items[k]['k'] == 'p':
                    lines.append(items[k]['text'].rstrip())
            blocks.append(dict(t='diagram', lines=lines, src=(sa, sb)))
            i = sb + 1
            continue
        if it.get('bold'):
            blocks.append(dict(t='h3', text=s.strip()))
            i += 1
            continue
        if it.get('list'):
            lis = []
            while i <= b and items[i]['k'] == 'p' and (items[i].get('list') or is_blank(items[i]['text'])) and i not in span_of:
                if not is_blank(items[i]['text']):
                    lis.append(items[i]['text'].strip())
                i += 1
            blocks.append(dict(t='ul', items=lis))
            continue
        blocks.append(dict(t='p', text=s.strip()))
        i += 1
    return blocks

doc = []
for p in parts:
    pn = p['part']['no']
    entry = dict(no=pn, title=p['part']['title'], subtitle=p['part']['subtitle'],
                 intro=render_range(*p['intro']), chapters=[])
    secmap = {s['no']: s for s in p['sections']}
    for ci, (ctitle, lo, hi) in enumerate(CHAPTERS[pn], 1):
        ch = dict(no=ci, title=ctitle, sections=[])
        for n in range(lo, hi + 1):
            if n in secmap:
                s = secmap[n]
                ch['sections'].append(dict(no=n, title=s['title'],
                                           blocks=render_range(s['start'], s['end'])))
        entry['chapters'].append(ch)
    # trailing sections beyond chapter map
    covered = set()
    for _, lo, hi in CHAPTERS[pn]:
        covered.update(range(lo, hi + 1))
    extra = [s for s in p['sections'] if s['no'] not in covered]
    if extra:
        ch = dict(no=len(entry['chapters']) + 1, title='Appendix', sections=[])
        for s in extra:
            ch['sections'].append(dict(no=s['no'], title=s['title'],
                                       blocks=render_range(s['start'], s['end'])))
        entry['chapters'].append(ch)
    doc.append(entry)

json.dump(doc, open('doc.json', 'w'), ensure_ascii=False)

# stats
nd = 0
for p in doc:
    for blk in p['intro']:
        nd += blk['t'] == 'diagram'
    for ch in p['chapters']:
        for s in ch['sections']:
            for blk in s['blocks']:
                nd += blk['t'] == 'diagram'
print('parts', len(doc), 'diagrams', nd)
for p in doc:
    print(' part', p['no'], 'chapters', len(p['chapters']),
          'sections', sum(len(c['sections']) for c in p['chapters']))

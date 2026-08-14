"""ASCII-diagram -> designed SVG figure engine."""
import re, html, math

# ------------------------------------------------------------------ palette
INK      = '#1c2434'
MUTED    = '#5b6辆'  # placeholder replaced below
MUTED    = '#5d6b82'
LINE     = '#94a3b8'
BOX_BG   = '#ffffff'
BOX_BD   = '#c3ccda'
ACCENT   = '#1f5fa8'
ACC_BG   = '#eaf1fa'
ACC_BD   = '#9dbde0'
WARM     = '#a8571f'
WARM_BG  = '#fbf1e7'
WARM_BD  = '#e0bd9d'
GREEN    = '#1d6b53'
GREEN_BG = '#e8f4ef'
GREEN_BD = '#9dcbba'
CODE_BG  = '#f4f6f9'

FS_NODE = 12.5
FS_SUB  = 11.0
FS_EDGE = 10.5
FS_MONO = 12.5
LH      = 15.5
PADX    = 13
PADY    = 9
GAP_Y   = 30
GAP_X   = 22
MINW    = 96
MAXW    = 250

VERT   = '│|┃'
ARROWD = '▼↓'
ARROWU = '▲↑'
BOXCH  = '┌┐└┘├┤┬┴┼─═╔╗╚╝║╠╣╦╩╬┏┓┗┛━'
ALLCONN = VERT + ARROWD + ARROWU + BOXCH + '+-→←►◄/\\_'


def wsans(s, fs=FS_NODE, bold=False):
    k = 0.545 if not bold else 0.585
    w = 0
    for ch in s:
        if ch in 'iljI.,\'|:;!':
            w += 0.30
        elif ch in 'mwMW—':
            w += 0.90
        elif ch.isupper():
            w += 0.68
        else:
            w += k
    return w * fs


def wmono(s, fs=FS_MONO):
    return len(s) * fs * 0.601


def norm(s):
    s = re.sub(r'-{2,}>', ' \u2192 ', s)
    s = re.sub(r'<-{2,}', ' \u2190 ', s)
    s = re.sub(r'\.{3,}>', ' \u2192 ', s)
    s = re.sub(r'[-\.]{3,}', ' \u2014 ', s)
    s = re.sub(r'\s*\u2192\s*', ' \u2192 ', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


def esc(s):
    return html.escape(s, quote=False)


# ------------------------------------------------------------------ parsing
def clean(lines):
    out = [l.rstrip() for l in lines]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return [l for l in out if l.strip()]


def is_border(l):
    t = l.strip()
    if len(t) < 3:
        return False
    return all(c in '┌┐└┘├┤┬┴┼─═╔╗╚╝╠╣╦╩╬┏┓┗┛━+-' for c in t) and any(c in '─-═━' for c in t)


def is_pure_conn(l):
    t = l.strip()
    return bool(t) and all(c in ALLCONN or c == ' ' for c in t)


def conn_cols(l):
    return [i for i, c in enumerate(l) if c in VERT + ARROWD + ARROWU]


def has_arrow(l):
    return any(c in ARROWD + ARROWU for c in l)


def unwrap_boxes(lines):
    """Detect ┌──┐ ... └──┘ (or +--+) boxes and turn their contents into plain
    node lines, remembering which lines were boxed."""
    n = len(lines)
    boxed = [False] * n
    drop = [False] * n
    i = 0
    while i < n:
        l = lines[i]
        m = re.match(r'^(\s*)([┌╔┏+])([─═━\-]{2,})([┐╗┓+])\s*$', l)
        if m:
            c0 = len(m.group(1))
            c1 = c0 + 1 + len(m.group(3))
            # find bottom
            j = i + 1
            body = []
            while j < n:
                lj = lines[j]
                if len(lj) > c0 and lj[c0] in '└╚┗+' and re.match(
                        r'^[─═━\-┬┴┼+]+[┘╝┛+]', lj[c0 + 1:c1 + 1] + '?'):
                    break
                if len(lj) > c0 and lj[c0] in VERT:
                    body.append(j)
                    j += 1
                    continue
                j = -1
                break
            if j != -1 and j < n and body:
                for b in body:
                    inner = lines[b][c0 + 1:c1]
                    lines[b] = inner
                    boxed[b] = True
                    if not inner.strip():
                        drop[b] = True
                drop[i] = True
                # bottom line may carry an exit tee
                bl = lines[j]
                seg = bl[c0:c1 + 1]
                if any(c in '┬┴┼' for c in seg) or seg.count('+') > 2:
                    pos = c0 + max((k for k, c in enumerate(seg) if c in '┬┴┼'),
                                   default=(c1 - c0) // 2)
                    lines[j] = ' ' * pos + '│'
                else:
                    drop[j] = True
                i = j
                continue
        i += 1
    res, resb = [], []
    for k in range(n):
        if drop[k] or not lines[k].strip():
            continue
        res.append(lines[k])
        resb.append(boxed[k])
    return res, resb


def split_cells(l):
    """Split a node line into cells separated by >=3 spaces."""
    cells = []
    l = l.rstrip()
    for m in re.finditer(r'\S(?:.*?\S)?(?=\s{3,}|$)', l):
        t = m.group(0).strip()
        if t:
            cells.append((t, m.start(), m.start() + len(m.group(0))))
    return cells


# ------------------------------------------------------------------ special shapes
BRANCH_RE = re.compile(r'^([\s│|]*)([├└])[─-]{1,}\s*(.*)$')


def detect_annotation(lines):
    """digits/string on line 0, then └── / ├── pointers to labels."""
    if len(lines) < 2:
        return None
    head = lines[0]
    if is_pure_conn(head) or is_border(head):
        return None
    ptrs = []
    for l in lines[1:]:
        m = BRANCH_RE.match(l)
        if m:
            ptrs.append((len(m.group(1)), m.group(3).strip()))
        elif is_pure_conn(l):
            continue
        else:
            return None
    if not ptrs:
        return None
    cols = [c for c, _ in ptrs]
    if len(set(cols)) < 2 and len(ptrs) > 1:
        return None          # same column -> tree, not annotation
    if len(ptrs) == 1 and cols[0] > len(head):
        return None
    if max(cols) > len(head) + 2:
        return None
    return dict(kind='annot', head=head, ptrs=sorted(ptrs))


def detect_tree(lines):
    """root then >=2 sibling ├──/└── at the same column."""
    if len(lines) < 3:
        return None
    root = lines[0]
    if is_pure_conn(root) or is_border(root):
        return None
    kids, cols = [], []
    for l in lines[1:]:
        m = BRANCH_RE.match(l)
        if m:
            kids.append(m.group(3).strip())
            cols.append(len(m.group(1)))
        elif is_pure_conn(l):
            continue
        else:
            return None
    if len(kids) < 2 or len(set(cols)) != 1:
        return None
    return dict(kind='tree', root=root.strip(), kids=kids)


STACK_B = re.compile(r'^\s*[+┌└├╔╠][-─═]{2,}[+┐┘┤╗╣]\s*$')
STACK_C = re.compile(r'^\s*[|│║](.*)[|│║]\s*$')


def detect_stack(lines):
    if len(lines) < 5:
        return None
    layers = []
    expect = 'b'
    for l in lines:
        if expect == 'b':
            if not STACK_B.match(l):
                return None
            expect = 'c'
        else:
            m = STACK_C.match(l)
            if not m:
                if STACK_B.match(l):
                    continue
                return None
            t = m.group(1).strip()
            if not t:
                return None
            layers.append(t)
            expect = 'b'
    if len(layers) < 2 or not STACK_B.match(lines[-1]):
        return None
    return dict(kind='stack', layers=layers)


def render_stack(spec):
    layers = spec['layers']
    W = min(430, max(240, max(wsans(t, FS_NODE, True) for t in layers) + 110))
    bh = 30
    H = 10 + bh * len(layers) + 10
    out = [svg_open(W, H), defs()]
    x = 10
    bw = W - 20
    for i, t in enumerate(layers):
        y = 8 + i * bh
        top = i == 0
        bot = i == len(layers) - 1
        shade = ACC_BG if i % 2 == 0 else '#f7f9fc'
        out.append(rect(x, y, bw, bh, shade, ACC_BD if i % 2 == 0 else BOX_BD,
                        rx=0, sw=1))
        out.append(text_el(x + bw / 2, y + bh / 2 + 4.4, norm(t), FS_NODE,
                           ACCENT if i % 2 == 0 else INK, weight='600'))
    out.append(rect(x, 8, bw, bh * len(layers), 'none', '#8ea6c4', rx=4, sw=1.4))
    out.append('</svg>')
    return ''.join(out)


MAP_RE = re.compile(r'^\s*(.+?)\s*(→|->|=|≠)\s*(.+?)\s*$')


def detect_map(lines):
    rows = []
    for l in lines:
        if is_pure_conn(l) or is_border(l):
            return None
        m = MAP_RE.match(l)
        if not m or any(c in BOXCH for c in l):
            return None
        rows.append((m.group(1), m.group(2), m.group(3)))
    if len(rows) < 2:
        return None
    return dict(kind='map', rows=rows)


# ------------------------------------------------------------------ chain model
def build_rows(lines, boxed):
    """Turn cleaned lines into a vertical sequence of rows + edges."""
    n = len(lines)
    from collections import Counter
    _cc = Counter()
    for l in lines:
        if is_pure_conn(l):
            for c in conn_cols(l):
                _cc[c] += 1
    axis = _cc.most_common(1)[0][0] if _cc else None
    rows = []          # {cells:[{lines:[],cx:float,boxed:bool}], bullets:[]}
    edges = []         # edge before row i: {label, arrow(bool)}
    pending = dict(label=None, arrow=False, seen=False)
    i = 0
    while i < n:
        l = lines[i]
        if is_border(l):
            pending['seen'] = True
            pending['arrow'] = pending['arrow'] or has_arrow(l)
            i += 1
            continue
        m = BRANCH_RE.match(l)
        if m and rows:
            rows[-1].setdefault('bullets', []).append(m.group(3).strip())
            i += 1
            continue
        if is_pure_conn(l):
            pending['seen'] = True
            if has_arrow(l):
                pending['arrow'] = True
            i += 1
            continue
        # connector + short label
        m2 = re.match(r'^\s*([' + VERT + ARROWD + ARROWU + r'])\s+(\S.{0,44})$', l)
        if m2 and rows and not any(c in BOXCH for c in m2.group(2)) \
                and not any(c in VERT for c in m2.group(2)):
            pending['seen'] = True
            pending['label'] = (pending['label'] + ' ' if pending['label'] else '') + m2.group(2).strip()
            if m2.group(1) in ARROWD + ARROWU:
                pending['arrow'] = True
            i += 1
            continue
        cells = split_cells(l)
        if not cells:
            i += 1
            continue
        cur = [dict(lines=[t], c0=a, c1=b, boxed=boxed[i]) for t, a, b in cells]
        # merge following aligned node lines
        j = i + 1
        while j < n:
            lj = lines[j]
            if is_border(lj) or is_pure_conn(lj) or BRANCH_RE.match(lj):
                break
            cj = split_cells(lj)
            if len(cj) != len(cur):
                break
            if len(cur) == 1 and not (boxed[i] and boxed[j]):
                break
            ok = True
            for k, (t, a, b) in enumerate(cj):
                if abs((a + b) / 2 - (cur[k]['c0'] + cur[k]['c1']) / 2) > 5:
                    ok = False
                    break
            if not ok:
                break
            for k, (t, a, b) in enumerate(cj):
                cur[k]['lines'].append(t)
                cur[k]['c0'] = min(cur[k]['c0'], a)
                cur[k]['c1'] = max(cur[k]['c1'], b)
                cur[k]['boxed'] = cur[k]['boxed'] or boxed[j]
            j += 1
        rows.append(dict(cells=cur, bullets=[]))
        edges.append(dict(label=pending['label'],
                          arrow=pending['arrow'],
                          link=pending['seen']))
        pending = dict(label=None, arrow=False, seen=False)
        i = j
    return rows, edges


# ------------------------------------------------------------------ svg helpers
def svg_open(w, h, cls='fig'):
    return (f'<svg class="{cls}" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img">')


def defs():
    return (
        '<defs>'
        f'<marker id="ah" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="7.5" '
        f'markerHeight="7.5" orient="auto-start-reverse">'
        f'<path d="M0.5 1.2 L9.4 5 L0.5 8.8 Z" fill="{LINE}"/></marker>'
        f'<marker id="ahd" viewBox="0 0 10 10" refX="9.2" refY="5" markerWidth="7.5" '
        f'markerHeight="7.5" orient="auto-start-reverse">'
        f'<path d="M0.5 1.2 L9.4 5 L0.5 8.8 Z" fill="{ACCENT}"/></marker>'
        '</defs>')


def text_el(x, y, s, fs=FS_NODE, fill=INK, anchor='middle', weight='500',
            family='ui-sans', mono=False, ls='0'):
    fam = ("'DejaVu Sans Mono',monospace" if mono
           else "'TeX Gyre Heros','Liberation Sans',sans-serif")
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{fs:.1f}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}">{esc(s)}</text>')


def rect(x, y, w, h, fill, stroke, rx=7, sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, dashed=False, accent=False):
    d = ' stroke-dasharray="4 3"' if dashed else ''
    mk = 'ahd' if accent else 'ah'
    col = ACCENT if accent else LINE
    return (f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" fill="none" '
            f'stroke="{col}" stroke-width="1.4"{d} marker-end="url(#{mk})"/>')


def polyline(pts, dashed=False, marker=False):
    d = ' stroke-dasharray="4 3"' if dashed else ''
    m = ' marker-end="url(#ah)"' if marker else ''
    p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    return (f'<polyline points="{p}" fill="none" stroke="{LINE}" '
            f'stroke-width="1.4" stroke-linejoin="round"{d}{m}/>')


# ------------------------------------------------------------------ node style
CAPS_RE = re.compile(r'^[^a-z]*$')


def node_style(lines_):
    t = ' '.join(lines_)
    core = re.sub(r'[^A-Za-z]', '', t)
    if core and CAPS_RE.match(t) and len(core) > 1:
        return ACC_BG, ACC_BD, ACCENT, '650'
    if re.match(r'^\+?\d[\d\s\-A-Zx]*$', t.strip()) or t.strip().startswith('+91') \
            or t.strip().startswith('+1 '):
        return WARM_BG, WARM_BD, WARM, '600'
    return BOX_BG, BOX_BD, INK, '500'


def is_monoish(t):
    return bool(re.match(r'^[+\d][\d\s\-XxYyA-Z().]*$', t.strip())) or \
        bool(re.search(r'(sip:|@|\bSIP/2\.0\b|::|/\d)', t))


# ------------------------------------------------------------------ renderers
def _wrap_columns(rows, edges):
    n = len(rows)
    ncols = 2 if n <= 26 else 3
    per = math.ceil(n / ncols)
    cols = [(i, min(i + per, n)) for i in range(0, n, per)]
    return cols


def render_chain(rows, edges, width_limit=486):
    # measure
    for r in rows:
        for c in r['cells']:
            tw = max(wsans(t, FS_NODE, True) for t in c['lines'])
            bw = 0
            if r.get('bullets') and len(r['cells']) == 1:
                bw = max((wsans('•  ' + b, FS_SUB) for b in r['bullets']), default=0)
            mw = MINW if len(r['cells']) <= 3 else 56
            c['w'] = max(mw, min(MAXW, max(tw, bw) + 2 * PADX))
            c['h'] = len(c['lines']) * LH + 2 * PADY
            if r.get('bullets') and len(r['cells']) == 1:
                c['h'] += len(r['bullets']) * (LH - 1) + 6
    # uniform width for single-cell rows (cleaner flowchart look)
    singles = [r['cells'][0] for r in rows if len(r['cells']) == 1]
    if len(singles) >= 2:
        uw = min(MAXW + 40, max(c['w'] for c in singles))
        for c in singles:
            c['w'] = uw
    # row widths
    for r in rows:
        r['w'] = sum(c['w'] for c in r['cells']) + GAP_X * (len(r['cells']) - 1)
        r['h'] = max(c['h'] for c in r['cells'])
    lblw = max((wsans(e['label'], FS_EDGE) for e in edges if e.get('label')), default=0)
    W = max(max(r['w'] for r in rows) + 16, 240)
    if lblw:
        W = max(W, max(r['w'] for r in rows) / 2 + 8 + lblw + 34)
    W = min(W, 620)
    est = 12 + sum(r['h'] for r in rows) + GAP_Y * (len(rows) - 1)
    if est > 720 and len(rows) >= 10:
        return _render_columns(rows, edges)
    # positions
    y = 6
    for i, r in enumerate(rows):
        e = edges[i]
        if i > 0:
            y += GAP_Y if e['link'] else 12
            if e['label']:
                y += 3
        x = (W - r['w']) / 2
        for c in r['cells']:
            c['x'] = x
            c['y'] = y + (r['h'] - c['h']) / 2
            c['cx'] = x + c['w'] / 2
            x += c['w'] + GAP_X
        r['y'] = y
        y += r['h']
    H = y + 6

    out = [svg_open(W, H), defs()]
    # edges
    for i in range(1, len(rows)):
        e = edges[i]
        prev, cur = rows[i - 1], rows[i]
        y1 = prev['y'] + prev['h']
        y2 = cur['y']
        if not e['link'] and len(prev['cells']) == len(cur['cells']):
            continue
        pn, cn = len(prev['cells']), len(cur['cells'])
        if pn == cn:
            pairs = list(zip(prev['cells'], cur['cells']))
            for a, b in pairs:
                out.append(arrow(a['cx'], y1 + 1, b['cx'], y2 - 3))
        elif pn == 1:
            a = prev['cells'][0]
            mid = (y1 + y2) / 2
            out.append(polyline([(a['cx'], y1 + 1), (a['cx'], mid)]))
            xs = [c['cx'] for c in cur['cells']]
            out.append(polyline([(min(xs), mid), (max(xs), mid)]))
            for b in cur['cells']:
                out.append(arrow(b['cx'], mid, b['cx'], y2 - 3))
        elif cn == 1:
            b = cur['cells'][0]
            mid = (y1 + y2) / 2
            for a in prev['cells']:
                out.append(polyline([(a['cx'], y1 + 1), (a['cx'], mid)]))
            xs = [c['cx'] for c in prev['cells']]
            out.append(polyline([(min(xs), mid), (max(xs), mid)]))
            out.append(arrow(b['cx'], mid, b['cx'], y2 - 3))
        elif cn % pn == 0:
            g = cn // pn
            mid = (y1 + y2) / 2
            for k, a in enumerate(prev['cells']):
                grp = cur['cells'][k * g:(k + 1) * g]
                out.append(polyline([(a['cx'], y1 + 1), (a['cx'], mid)]))
                xs = [c['cx'] for c in grp]
                out.append(polyline([(min(xs), mid), (max(xs), mid)]))
                for b in grp:
                    out.append(arrow(b['cx'], mid, b['cx'], y2 - 3))
        else:
            for k in range(min(pn, cn)):
                out.append(arrow(prev['cells'][k]['cx'], y1 + 1,
                                 cur['cells'][k]['cx'], y2 - 3))
        if e['label']:
            lx = (prev['cells'][0]['cx'] + cur['cells'][0]['cx']) / 2
            ly = (y1 + y2) / 2
            lab = e['label']
            fs = FS_EDGE
            while wsans(lab, fs) > W - lx - 18 and fs > 7.2:
                fs -= 0.3
            out.append(text_el(lx + 11, ly + 3.4, lab, fs, MUTED,
                               anchor='start', weight='500'))
    # nodes
    for r in rows:
        for c in r['cells']:
            bg, bd, fg, wt = node_style(c['lines'])
            out.append(rect(c['x'], c['y'], c['w'], c['h'], bg, bd))
            ty = c['y'] + PADY + 11.4
            for t in c['lines']:
                mono = is_monoish(t)
                if not mono:
                    t = norm(t)
                fs = FS_NODE
                avail = c['w'] - 2 * PADX + 6
                wfun = (lambda s: wmono(s, fs)) if mono else (lambda s: wsans(s, fs, True))
                while wfun(t) > avail and fs > 8.4:
                    fs -= 0.4
                out.append(text_el(c['cx'], ty, t, fs, fg, weight=wt, mono=mono))
                ty += LH
            if r.get('bullets') and len(r['cells']) == 1:
                ty += 3
                for b in r['bullets']:
                    out.append(f'<circle cx="{c["x"] + PADX + 3:.1f}" cy="{ty - 4:.1f}" '
                               f'r="1.9" fill="{LINE}"/>')
                    out.append(text_el(c['x'] + PADX + 11, ty, norm(b), FS_SUB, MUTED,
                                       anchor='start', weight='400'))
                    ty += LH - 1
    out.append('</svg>')
    return ''.join(out)


def render_annot(spec):
    head = spec['head']
    ptrs = sorted(spec['ptrs'], key=lambda p: p[0])
    cw = FS_MONO * 0.601
    x0 = 14
    hw = wmono(head)
    # all labels share one left edge, clear of every leader stem, so no
    # vertical line ever crosses a label
    maxcol = max(c for c, _ in ptrs)
    labx = x0 + maxcol * cw + cw / 2 + 26
    labw = max(wsans(l, FS_SUB) for _, l in ptrs)
    W = min(560, max(300, x0 - 8 + hw + 16, labx + labw + 14))
    rowh = 24
    H = 44 + rowh * len(ptrs) + 6
    out = [svg_open(W, H), defs()]
    out.append(rect(x0 - 8, 8, hw + 16, 28, CODE_BG, '#e2e8f0', rx=5, sw=1))
    out.append(text_el(x0, 28, head, FS_MONO, INK, anchor='start',
                       weight='600', mono=True))
    for k, (col, lab) in enumerate(ptrs):
        cx = x0 + col * cw + cw / 2
        yy = 44 + k * rowh
        out.append(polyline([(cx, 38), (cx, yy), (labx - 8, yy)]))
        out.append(f'<circle cx="{cx:.1f}" cy="{yy:.1f}" r="2.4" fill="{ACCENT}"/>')
        out.append(text_el(labx, yy + 3.8, lab, FS_SUB, MUTED,
                           anchor='start', weight='500'))
    out.append('</svg>')
    return ''.join(out)


def render_tree(spec):
    root, kids = spec['root'], spec['kids']
    rw = max(MINW, wsans(root, FS_NODE, True) + 2 * PADX)
    kw = max(140, min(300, max(wsans(k, FS_SUB) for k in kids) + 2 * PADX))
    rowh = 27
    W = min(520, max(rw + 40, 40 + 26 + kw + 20))
    H = 12 + 30 + rowh * len(kids) + 8
    out = [svg_open(W, H), defs()]
    bg, bd, fg, wt = node_style([root])
    out.append(rect(16, 8, rw, 28, bg, bd))
    out.append(text_el(16 + rw / 2, 27, root, FS_NODE, fg, weight=wt))
    stem = 16 + 20
    ys = []
    for k, kid in enumerate(kids):
        yy = 36 + 18 + k * rowh
        ys.append(yy)
        out.append(polyline([(stem, yy), (stem + 20, yy)]))
        out.append(rect(stem + 20, yy - 12, kw, 24, BOX_BG, BOX_BD, rx=5, sw=1))
        fs = FS_SUB
        while wsans(kid, fs) > kw - 18 and fs > 8:
            fs -= 0.3
        out.append(text_el(stem + 30, yy + 3.8, kid, fs, INK, anchor='start', weight='500'))
    out.append(polyline([(stem, 36), (stem, ys[-1])]))
    out.append('</svg>')
    return ''.join(out)


def render_map(spec):
    rows = spec['rows']
    lw = max(wsans(a, FS_NODE, True) for a, _, _ in rows)
    rw = max(wsans(c, FS_NODE) for _, _, c in rows)
    W = min(520, max(280, 20 + lw + 46 + rw + 20))
    rowh = 27
    H = 10 + rowh * len(rows) + 6
    lx = 18 + lw
    out = [svg_open(W, H), defs()]
    for k, (a, op, c) in enumerate(rows):
        y = 12 + k * rowh
        if k % 2 == 0:
            out.append(f'<rect x="6" y="{y - 1:.1f}" width="{W - 12:.1f}" height="{rowh - 3}" '
                       f'rx="4" fill="#f7f9fc"/>')
        out.append(text_el(lx, y + 15, a, FS_NODE, INK, anchor='end', weight='600'))
        sym = {'->': '→', '→': '→', '=': '=', '≠': '≠'}.get(op, op)
        out.append(text_el(lx + 22, y + 15, sym, FS_NODE, ACCENT, weight='600'))
        out.append(text_el(lx + 40, y + 15, c, FS_NODE, MUTED, anchor='start', weight='500'))
    out.append('</svg>')
    return ''.join(out)


def render_verbatim(lines):
    """Fallback: monospace panel, still styled."""
    fs = 11.0
    cw = fs * 0.601
    lh = 15.0
    maxlen = max(len(l) for l in lines)
    while maxlen * cw > 486 - 24 and fs > 6.4:
        fs -= 0.25
        cw = fs * 0.601
    W = min(520, max(240, maxlen * cw + 26))
    H = len(lines) * lh + 22
    out = [svg_open(W, H)]
    out.append(rect(1, 1, W - 2, H - 2, CODE_BG, '#e2e8f0', rx=6, sw=1))
    y = 11 + fs
    for l in lines:
        out.append(f'<text x="13" y="{y:.1f}" font-family="\'DejaVu Sans Mono\',monospace" '
                   f'font-size="{fs:.2f}" fill="{INK}" xml:space="preserve">{esc(l)}</text>')
        y += lh
    out.append('</svg>')
    return ''.join(out)


# ------------------------------------------------------------------ captions
def _cap_text(t):
    t = t.strip().rstrip('.').strip()
    if not t:
        return t
    if t.isupper() and ' ' in t and len(re.sub(r'[^A-Za-z]', '', t)) > 3:
        t = t[0] + t[1:].lower()
    return t


def caption_for(kind, data):
    if kind == 'annot':
        return 'Structure of %s' % data['head'].strip()
    if kind == 'tree':
        return '%s and its constituent parts' % _cap_text(data['root'])
    if kind == 'chain':
        rows = data
        first = ' / '.join(rows[0]['cells'][k]['lines'][0] for k in range(len(rows[0]['cells'])))
        last = ' / '.join(rows[-1]['cells'][k]['lines'][0] for k in range(len(rows[-1]['cells'])))
        first, last = _cap_text(first), _cap_text(last)
        mid = ''
        if len(rows) >= 5:
            m = rows[len(rows) // 2]
            mid = _cap_text(' / '.join(c['lines'][0] for c in m['cells']))
        if first.lower() == last.lower():
            return '%s, end to end' % first if not mid else \
                   '%s \u2192 %s \u2192 %s' % (first, mid, first)
        if mid and mid.lower() not in (first.lower(), last.lower()):
            return '%s \u2192 %s \u2192 %s' % (first, mid, last)
        return '%s \u2192 %s' % (first, last)
    return 'Diagram'


# ------------------------------------------------------------------ entry point
def make_figure(lines):
    src = clean(lines)
    if not src:
        return None, 'empty'
    spec = detect_annotation(src)
    if spec:
        return render_annot(spec), 'annot', caption_for('annot', spec)
    spec = detect_tree(src)
    if spec:
        return render_tree(spec), 'tree', caption_for('tree', spec)
    spec = detect_stack(src)
    if spec:
        return (render_stack(spec), 'stack',
                'Encapsulation stack: %s over %s'
                % (spec['layers'][0], spec['layers'][-1]))
    spec = detect_map(src)
    if spec:
        return render_map(spec), 'map', 'Mapping'
    work = list(src)
    work, boxed = unwrap_boxes(work)
    if not work:
        return render_verbatim(src), 'verbatim', 'Diagram'
    rows, edges = build_rows(work, boxed)
    if not rows:
        return render_verbatim(src), 'verbatim', 'Diagram'
    if max(len(r['cells']) for r in rows) > 6:
        return render_verbatim(src), 'verbatim', 'Diagram'
    if len(rows) == 1 and len(rows[0]['cells']) == 1 and not rows[0].get('bullets'):
        return ' \u2014 '.join(rows[0]['cells'][0]['lines']), 'inline', None
    cap = caption_for('chain', rows)
    return render_chain(rows, edges), 'chain', cap


def _render_columns(rows, edges):
    n = len(rows)
    ncols = 2
    if n > 22:
        ncols = 3
    per = math.ceil(n / ncols)
    groups = [rows[i:i + per] for i in range(0, n, per)]
    ncols = len(groups)
    colgap = 44
    nw = min(MAXW, max(r['w'] for r in rows))
    total = ncols * nw + (ncols - 1) * colgap
    if total > 646:
        nw = (646 - (ncols - 1) * colgap) / ncols
        total = 646
    W = total + 20
    gy = 26
    # scale each row's cells into column width
    for r in rows:
        k = len(r['cells'])
        avail = nw - GAP_X * (k - 1)
        sc = min(1.0, avail / max(1e-6, sum(c['w'] for c in r['cells'])))
        for c in r['cells']:
            c['w'] = c['w'] * sc
    heights = []
    for g in groups:
        h = 8 + sum(r['h'] for r in g) + gy * (len(g) - 1)
        heights.append(h)
    H = max(heights) + 18

    out = [svg_open(W, H), defs()]
    for ci, g in enumerate(groups):
        x0 = 10 + ci * (nw + colgap)
        y = 10
        for k, r in enumerate(g):
            rw = sum(c['w'] for c in r['cells']) + GAP_X * (len(r['cells']) - 1)
            x = x0 + (nw - rw) / 2
            for c in r['cells']:
                c['x'] = x
                c['y'] = y + (r['h'] - c['h']) / 2
                c['cx'] = x + c['w'] / 2
                x += c['w'] + GAP_X
            r['y'] = y
            if k:
                prev = g[k - 1]
                y1 = prev['y'] + prev['h']
                pn, cn = len(prev['cells']), len(r['cells'])
                if pn == cn:
                    for a, b in zip(prev['cells'], r['cells']):
                        out.append(arrow(a['cx'], y1 + 1, b['cx'], y - 3))
                elif pn == 1:
                    a = prev['cells'][0]
                    mid = (y1 + y) / 2
                    xs = [c['cx'] for c in r['cells']]
                    out.append(polyline([(a['cx'], y1 + 1), (a['cx'], mid)]))
                    out.append(polyline([(min(xs), mid), (max(xs), mid)]))
                    for b in r['cells']:
                        out.append(arrow(b['cx'], mid, b['cx'], y - 3))
                else:
                    b = r['cells'][0]
                    mid = (y1 + y) / 2
                    xs = [c['cx'] for c in prev['cells']]
                    for a in prev['cells']:
                        out.append(polyline([(a['cx'], y1 + 1), (a['cx'], mid)]))
                    out.append(polyline([(min(xs), mid), (max(xs), mid)]))
                    out.append(arrow(b['cx'], mid, b['cx'], y - 3))
                gi = ci * per + k
                lab = edges[gi]['label'] if gi < len(edges) else None
                if lab:
                    fs = FS_EDGE
                    while wsans(lab, fs) > colgap + 30 and fs > 7:
                        fs -= 0.3
                    out.append(text_el(r['cells'][0]['cx'] + 9, y - gy / 2 + 3.4,
                                       lab, fs, MUTED, anchor='start', weight='500'))
            y += r['h'] + gy
        if ci + 1 < ncols:
            last = g[-1]['cells'][-1]
            nxt = groups[ci + 1][0]['cells'][0]
            xb = 10 + (ci + 1) * (nw + colgap) + nw / 2
            ybot = g[-1]['y'] + g[-1]['h']
            xm = x0 + nw + colgap / 2
            out.append(polyline([(last['cx'], ybot + 2), (last['cx'], ybot + 13),
                                 (xm, ybot + 13), (xm, 4), (xb, 4), (xb, 8)],
                                dashed=True, marker=True))
    for r in rows:
        for c in r['cells']:
            bg, bd, fg, wt = node_style(c['lines'])
            out.append(rect(c['x'], c['y'], c['w'], c['h'], bg, bd))
            ty = c['y'] + PADY + 11.4
            for t in c['lines']:
                mono = is_monoish(t)
                if not mono:
                    t = norm(t)
                fs = FS_NODE
                avail = c['w'] - 2 * PADX + 6
                wf = (lambda z: wmono(z, fs)) if mono else (lambda z: wsans(z, fs, True))
                while wf(t) > avail and fs > 7.6:
                    fs -= 0.35
                out.append(text_el(c['cx'], ty, t, fs, fg, weight=wt, mono=mono))
                ty += LH
            if r.get('bullets') and len(r['cells']) == 1:
                ty += 3
                for b in r['bullets']:
                    fs = FS_SUB
                    while wsans('\u2022 ' + b, fs) > c['w'] - 2 * PADX and fs > 7:
                        fs -= 0.3
                    out.append(text_el(c['x'] + PADX, ty, '\u2022 ' + b, fs, MUTED,
                                       anchor='start', weight='400'))
                    ty += LH - 1
    out.append('</svg>')
    return ''.join(out)

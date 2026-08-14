"""Build the three volume PDFs."""
import json, re, html, sys
import figures
import gloss_render

doc = json.load(open('doc.json'))

ROMAN = ['', 'I', 'II', 'III']
VOLNAME = {1: 'Volume I', 2: 'Volume II', 3: 'Volume III'}

BOOK_TITLE = 'The Anatomy of a Phone Number'
BOOK_SUB = 'A layered study of telephone numbering, mobile networks and packet telephony'

VOL_BLURB = {
 1: ('Why a telephone number is an identifier rather than an address, how the '
     'international numbering plan is organised, what the SIM, the handset and the '
     'subscription each contribute, and how 150 years of switching technology changed '
     'underneath a string of digits that barely changed at all.'),
 2: ('A single 5G Standalone voice call, followed end to end: cell search, registration, '
     'authentication, PDU sessions, IMS registration, the SIP INVITE, inter-operator '
     'routing, paging, codec negotiation, QoS and the radio stack that finally carries '
     'the speech.'),
 3: ('The same call at packet granularity: SIP and SDP field by field, GTP-U tunnelling, '
     'PDCP/RLC/MAC/PHY, the RTP header, jitter and loss, the control-plane stack, and the '
     'point at which the telephone number stops existing on the wire.'),
}

MOTIF = {
 1: ['NUMBER', 'IDENTITY', 'NETWORK', 'LOCATION', 'RADIO'],
 2: ['REGISTER', 'AUTHENTICATE', 'INVITE', 'PAGE', 'ANSWER', 'RTP'],
 3: ['SIP', 'SDP', 'IP', 'GTP-U', 'PDCP', 'RLC', 'MAC', 'PHY'],
}

VOL_LIST = [
 (1, 'The Architecture of a Phone Number'),
 (2, 'Anatomy of a 5G Voice Call'),
 (3, 'Packet-Level Telecommunications'),
]

SRC_TAG = re.compile(r'\s*\((FCC Complaints|ITU|3GPP Portal|RFC Editor|NANPA|TRAI|GSMA)\)\s*$')
MAPLINE = re.compile(r'^\s*(.{1,46}?)\s*(→|->|≠|=)\s*(.+?)\s*$')


def esc(t):
    return html.escape(t, quote=False)


def rich(t):
    t = esc(t)
    t = re.sub(r'\(((?:FCC Complaints|ITU|3GPP Portal|RFC Editor|NANPA|TRAI|GSMA))\)',
               r'<span class="src">\1</span>', t)
    return t


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]


# ------------------------------------------------------------------ block rendering
def group_maps(blocks):
    """Fold runs of 'X → Y' paragraphs into a single deflist block."""
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b['t'] == 'p':
            m = MAPLINE.match(b['text'])
            if m and len(b['text']) < 90:
                run = []
                j = i
                while j < len(blocks) and blocks[j]['t'] == 'p':
                    mm = MAPLINE.match(blocks[j]['text'])
                    if not mm or len(blocks[j]['text']) >= 90:
                        break
                    run.append((mm.group(1), mm.group(2), mm.group(3)))
                    j += 1
                if len(run) >= 3:
                    out.append(dict(t='deflist', rows=run))
                    i = j
                    continue
        out.append(b)
        i += 1
    return out


def group_refs(blocks):
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b['t'] == 'h3' and re.search(r'reference|standards worth', b['text'], re.I):
            out.append(b)
            j = i + 1
            run = []
            while j < len(blocks) and blocks[j]['t'] == 'p' and len(blocks[j]['text']) < 130 \
                    and not blocks[j]['text'].endswith(('.', '?')) or \
                    (j < len(blocks) and blocks[j]['t'] == 'p'
                     and re.match(r'^(ITU|ETSI|GSMA|NANPA|TRAI|3GPP|RFC)', blocks[j]['text'])):
                if not re.match(r'^(ITU|ETSI|GSMA|NANPA|TRAI|3GPP|RFC)', blocks[j]['text']):
                    break
                run.append(blocks[j]['text'])
                j += 1
            if run:
                out.append(dict(t='refs', items=run))
                i = j
                continue
        out.append(b)
        i += 1
    return out


LITERAL = re.compile(r'^(\+|\d|[A-Z0-9][A-Z0-9/._\-]*$)')


def _short(t):
    return len(t) <= 48 and not t.endswith(('.', ':', ',', ';', '?', '!'))


def _literal(t):
    if '→' in t or '≠' in t:
        return True
    if re.match(r'^[+\d]', t):
        return True
    if re.match(r'^[A-Za-z0-9][A-Za-z0-9/._\-]*$', t) and t.isupper():
        return True
    if re.match(r'^(sip:|INVITE|SIP/|Via:|To:|From:|Call-ID:|CSeq:|m=|c=|a=|v=|o=|s=|t=)', t):
        return True
    return False


def _junk(t):
    t = t.strip()
    return len(t) < 3 and not t.isalnum()


def group_shorts(blocks):
    blocks = [b for b in blocks if not (b['t'] == 'p' and _junk(b['text']))]
    out = []
    i = 0
    n = len(blocks)
    while i < n:
        b = blocks[i]
        if b['t'] == 'p' and _short(b['text']):
            j = i
            run = []
            while j < n and blocks[j]['t'] == 'p' and _short(blocks[j]['text']):
                run.append(blocks[j]['text'])
                j += 1
            if len(run) >= 2 and all(_literal(x) for x in run):
                out.append(dict(t='literal', lines=run))
                i = j
                continue
            if len(run) >= 3:
                out.append(dict(t='cols', items=run))
                i = j
                continue
            if len(run) == 1 and _literal(run[0]):
                out.append(dict(t='literal', lines=run))
                i = j
                continue
        out.append(b)
        i += 1
    return out


class Ctx:
    def __init__(self):
        self.chap = 0
        self.fig = 0
        self.tab = 0
        self.figlist = []


def render_blocks(blocks, ctx):
    blocks = group_maps(blocks)
    blocks = group_refs(blocks)
    blocks = group_shorts(blocks)
    out = []
    for b in blocks:
        t = b['t']
        if t == 'p':
            txt = b['text']
            if len(txt) < 4:
                continue
            cls = ''
            if txt.endswith(':') and len(txt) < 70:
                cls = ' class="lead"'
            out.append(f'<p{cls}>{rich(txt)}</p>')
        elif t == 'h3':
            s = b['text'].strip()
            if not s:
                continue
            if len(s) > 66:
                out.append(f'<p class="pull">{rich(s)}</p>')
            else:
                out.append(f'<h4>{esc(s)}</h4>')
        elif t == 'ul':
            lis = ''.join(f'<li>{rich(x)}</li>' for x in b['items'])
            out.append(f'<ul>{lis}</ul>')
        elif t == 'refs':
            lis = ''.join(f'<li>{rich(x)}</li>' for x in b['items'])
            out.append(f'<ul class="refs">{lis}</ul>')
        elif t == 'literal':
            body = '<br>'.join(esc(x) for x in b['lines'])
            out.append(f'<p class="callout">{body}</p>')
        elif t == 'cols':
            mx = max(len(x) for x in b['items'])
            cls = 'cols3' if mx <= 24 else ('cols2' if mx <= 42 else 'cols1')
            lis = ''.join(f'<li>{rich(x)}</li>' for x in b['items'])
            out.append(f'<ul class="tight {cls}">{lis}</ul>')
        elif t == 'deflist':
            if all(len(a.strip()) <= 2 for a, _, _ in b['rows']):
                code = '<br>'.join(f'{esc(a)}{esc(op)}{esc(c)}' for a, op, c in b['rows'])
                out.append(f'<p class="callout">{code}</p>')
                continue
            rows = ''.join(
                f'<tr><td class="dk">{esc(a)}</td><td class="dop">{esc(op)}</td>'
                f'<td class="dv">{esc(c)}</td></tr>' for a, op, c in b['rows'])
            out.append(f'<table class="deflist">{rows}</table>')
        elif t == 'table':
            ctx.tab += 1
            rows = b['rows']
            head = ''.join(f'<th>{esc(c)}</th>' for c in rows[0])
            body = ''.join('<tr>' + ''.join(f'<td>{rich(c)}</td>' for c in r) + '</tr>'
                           for r in rows[1:])
            out.append(f'<figure class="tbl"><table class="data"><thead><tr>{head}</tr>'
                       f'</thead><tbody>{body}</tbody></table>'
                       f'<figcaption><span class="lab">Table {ctx.chap}.{ctx.tab}</span></figcaption>'
                       f'</figure>')
        elif t == 'diagram':
            svg, kind, cap = figures.make_figure(b['lines'])
            if svg is None:
                continue
            if kind == 'inline':
                out.append(f'<p class="callout">{esc(svg)}</p>')
                continue
            ctx.fig += 1
            num = f'{ctx.chap}.{ctx.fig}'
            fid = f'fig-{num.replace(".", "-")}'
            capt = (cap or '').strip()
            ctx.figlist.append((num, capt, fid))
            out.append(
                f'<figure class="fig" id="{fid}"><div class="figbody">{svg}</div>'
                f'<figcaption><span class="lab">Figure {num}</span>'
                f'{"&ensp;" + esc(capt) if capt else ""}</figcaption></figure>')
    return '\n'.join(out)


# ------------------------------------------------------------------ CSS
CSS = r"""
@page {
  size: A4;
  margin: 24mm 20mm 22mm 20mm;
  @bottom-center {
    content: counter(page);
    font-family: 'TeX Gyre Heros', sans-serif; font-size: 8.6pt; color: #8a94a3;
    padding-top: 5mm;
  }
  @top-center {
    content: string(runhead);
    font-family: 'TeX Gyre Heros', sans-serif; font-size: 7.8pt;
    letter-spacing: .09em; text-transform: uppercase; color: #a3abb8;
    padding-bottom: 5mm;
  }
}
@page cover { margin: 0; @bottom-center { content: none } @top-center { content: none } }
@page front { @top-center { content: none } }
@page chapopen { @top-center { content: none } }

html { font-family: 'Bitstream Charter', 'Charter', 'DejaVu Serif', serif;
       font-size: 10.4pt; line-height: 1.53; color: #1c2434; }
body { margin: 0; hyphens: auto; }

/* ---------- cover ---------- */
.cover { page: cover; height: 297mm; position: relative; color: #fff;
         background: #14243c; }
.cover .band { position: absolute; left: 0; right: 0; top: 0; height: 124mm;
               background: linear-gradient(135deg,#1f5fa8 0%, #14243c 100%); }
.cover .inner { position: absolute; left: 22mm; right: 22mm; top: 26mm; }
.cover .kicker { font-family: 'TeX Gyre Heros', sans-serif; font-size: 9.5pt;
                 letter-spacing: .30em; text-transform: uppercase; color: #9dc2ee; }
.cover h1 { font-family: 'TeX Gyre Heros', sans-serif; font-size: 29pt; line-height: 1.14;
            font-weight: 700; margin: 9mm 0 0; letter-spacing: -.012em; color:#fff; }
.cover .vol { font-family: 'TeX Gyre Heros', sans-serif; font-size: 11pt;
              letter-spacing: .22em; text-transform: uppercase; color: #7fb0e6;
              margin-top: 3mm; }
.cover .rule { width: 34mm; height: 3px; background: #6fa8e8; margin: 8mm 0 7mm; }
.cover .sub { font-size: 12.5pt; color: #c9d6e6; line-height: 1.45; max-width: 130mm;
              hyphens: none; }
.cover .blurb { position: absolute; left: 22mm; right: 24mm; top: 143mm;
                color: #46566d; font-size: 10.2pt; line-height: 1.6; max-width: 128mm; }
.cover .motif { position: absolute; left: 22mm; right: 22mm; top: 196mm; }
.cover .chip { display:inline-block; font-family:'TeX Gyre Heros',sans-serif;
               font-size: 8.2pt; letter-spacing:.13em; text-transform:uppercase;
               color:#46566d; border:1px solid #c3ccda; border-radius:3px;
               padding: 1.4mm 2.6mm; margin: 0 0 2mm; background:#fff; }
.cover .arw { color:#9dbde0; padding: 0 1.6mm; font-size: 9pt; }
.cover .booktitle { position: absolute; left: 22mm; right: 22mm; bottom: 30mm; color: #46566d;
                    font-family: 'TeX Gyre Heros', sans-serif; font-size: 9pt;
                    letter-spacing: .16em; text-transform: uppercase; }
.cover .set { position: absolute; left: 22mm; bottom: 21mm; text-align: left;
              color: #46566d; font-family: 'TeX Gyre Heros', sans-serif; font-size: 9pt;
              letter-spacing: .14em; text-transform: uppercase; }
.cover .lower { position: absolute; left:0; right:0; top: 124mm; bottom:0;
                background: #f4f6f9; }

/* ---------- front matter ---------- */
.front { page: front; }
h2.fm { font-family: 'TeX Gyre Heros', sans-serif; font-size: 17pt; font-weight: 700;
        letter-spacing: -.005em; margin: 0 0 2mm; color: #14243c; }
.fmrule { height: 2.5px; width: 22mm; background: #1f5fa8; margin: 0 0 7mm; }
.about p { margin: 0 0 3.6mm; }
.volcards { margin-top: 6mm; }
.volcard { border-left: 3px solid #c3ccda; padding: 1mm 0 1mm 5mm; margin: 0 0 4mm; }
.volcard.me { border-left-color: #1f5fa8; }
.volcard .n { font-family:'TeX Gyre Heros',sans-serif; font-size: 8.4pt;
              letter-spacing:.16em; text-transform: uppercase; color:#8a94a3; }
.volcard.me .n { color:#1f5fa8; }
.volcard .t { font-family:'TeX Gyre Heros',sans-serif; font-size: 11.4pt; font-weight:600;
              color:#14243c; }

/* ---------- contents ---------- */
ul.toc { list-style: none; margin: 0; padding: 0; }
ul.toc li { margin: 0; }
.toc .ch { display: flex; align-items: baseline; margin: 5.2mm 0 1.4mm;
           font-family: 'TeX Gyre Heros', sans-serif; }
.toc .ch .no { flex: 0 0 12mm; font-size: 8.6pt; letter-spacing: .12em;
               text-transform: uppercase; color: #1f5fa8; font-weight: 600; }
.toc .ch .ti { flex: 1 1 auto; font-size: 11.4pt; font-weight: 600; color: #14243c; }
.toc .ch .pg::after { content: target-counter(attr(href), page); }
.toc .ch .pg { font-size: 10pt; color: #14243c; font-weight: 600;
               text-decoration: none; }
.toc .sec { display: flex; align-items: baseline; margin: 0 0 .6mm 12mm;
            font-size: 9.4pt; color: #46566d; }
.toc .sec .ti { flex: 1 1 auto; }
.toc .sec .dots { flex: 1 1 auto; border-bottom: 1px dotted #ccd4e0;
                  margin: 0 2mm 1mm; min-width: 6mm; }
.toc .sec .pg { color: #6b7a90; text-decoration: none; }
.toc .sec .pg::after { content: target-counter(attr(href), page); }
.lof li { display: flex; align-items: baseline; font-size: 9.3pt; color:#46566d;
          margin: 0 0 1.2mm; }
.lof .no { flex: 0 0 17mm; font-family:'TeX Gyre Heros',sans-serif; font-size:8.6pt;
           color:#1f5fa8; font-weight:600; }
.lof .ti { flex: 1 1 auto; }
.lof .dots { flex: 0 1 auto; border-bottom:1px dotted #ccd4e0; margin: 0 2mm 1mm;
             min-width: 5mm; }
.lof .pg::after { content: target-counter(attr(href), page); }
.lof .pg { color:#6b7a90; text-decoration:none; }
ul.lof { list-style:none; margin:0; padding:0; }

/* ---------- chapter ---------- */
.chapter { break-before: page; }
.chapopen { page: chapopen; break-after: avoid; margin: 8mm 0 11mm; }
.chapopen .cno { font-family:'TeX Gyre Heros',sans-serif; font-size: 9pt;
                 letter-spacing:.26em; text-transform:uppercase; color:#1f5fa8;
                 font-weight:600; }
.chapopen h2 { font-family:'TeX Gyre Heros',sans-serif; font-size: 23pt; font-weight:700;
               line-height:1.16; margin: 3mm 0 0; color:#14243c; letter-spacing:-.012em;
               string-set: runhead content(); }
.chapopen .crule { height:3px; width:26mm; background:#1f5fa8; margin: 6mm 0 0; }
.chapopen .clist { margin-top: 6mm; column-count: 2; column-gap: 8mm;
                   font-size: 9pt; color:#5d6b82; }
.chapopen .clist div { margin: 0 0 1.3mm; break-inside: avoid; }
.chapopen .clist span { color:#1f5fa8; font-family:'TeX Gyre Heros',sans-serif;
                        font-size:8.2pt; font-weight:600; }

h3.sec { font-family:'TeX Gyre Heros',sans-serif; font-size: 12.6pt; font-weight:600;
         color:#14243c; margin: 8.5mm 0 2.6mm; break-after: avoid;
         line-height:1.28; }
h3.sec .n { color:#1f5fa8; font-size: 9.6pt; letter-spacing:.05em;
            margin-right: 2.2mm; }
h4 { font-family:'TeX Gyre Heros',sans-serif; font-size: 10pt; font-weight:600;
     letter-spacing:.05em; color:#1f5fa8; margin: 5mm 0 1.6mm; break-after: avoid; }

p { margin: 0 0 3.1mm; text-align: justify; }
p.lead { margin-bottom: 1.8mm; color:#46566d; }
p.pull { font-family:'TeX Gyre Heros',sans-serif; font-size: 11pt; line-height:1.45;
         color:#14243c; background:#eef3f9; border-left:3px solid #1f5fa8;
         padding: 3.4mm 4.5mm; margin: 4.5mm 0 4.5mm; text-align:left;
         break-inside: avoid; font-weight:500; }
p.callout { display:inline-block; max-width:100%; overflow-wrap:anywhere;
            font-family:'DejaVu Sans Mono',monospace; font-size: 9.4pt;
            background:#f4f6f9; border:1px solid #e2e8f0; border-radius:5px;
            padding: 2.4mm 3.4mm; margin: 3mm 0; text-align:left;
            break-inside: avoid; color:#14243c; }
ul { margin: 0 0 3.4mm; padding-left: 5.4mm; }
li { margin: 0 0 1.1mm; }
ul.refs { font-size: 9.5pt; color:#46566d; }
ul.tight { margin: 2.2mm 0 3.4mm; padding-left: 4.6mm; }
ul.tight li { margin: 0 0 .9mm; break-inside: avoid; }
ul.cols3 { column-count: 3; column-gap: 7mm; }
ul.cols2 { column-count: 2; column-gap: 8mm; }
.src { font-family:'TeX Gyre Heros',sans-serif; font-size: 7.6pt; color:#8a94a3;
       letter-spacing:.04em; }

/* ---------- glossary ---------- */
.chapopen .gnote { margin-top: 6mm; font-size: 9.4pt; color:#5d6b82; max-width: 120mm;
                   line-height:1.5; }
.gloss { column-count: 2; column-gap: 8mm; margin-top: 2mm; }
.gletter { font-family:'TeX Gyre Heros',sans-serif; font-size: 9pt; font-weight:700;
           letter-spacing:.18em; color:#1f5fa8; border-bottom:1.4px solid #c3ccda;
           padding-bottom: 1.2mm; margin: 4.6mm 0 2.6mm; break-after: avoid;
           break-inside: avoid; }
.gitem { margin: 0 0 3.1mm; break-inside: avoid; font-size: 9pt; line-height:1.45; }
.ghw { font-family:'TeX Gyre Heros',sans-serif; font-weight:600; font-size: 9.4pt;
       color:#14243c; }
.gexp { display:block; font-size: 8.4pt; font-style: italic; color:#8a94a3;
        margin: .3mm 0 .8mm; }
.gdef { display:block; color:#46566d; text-align: justify; hyphens: auto; }

/* ---------- figures ---------- */
figure.fig { margin: 5.5mm 0 5.5mm; break-inside: avoid; text-align: center; }
figure.fig .figbody { display:inline-block; background:#fdfdfe; border:1px solid #e6ebf2;
                      border-radius:8px; padding: 4.5mm 4mm 3.5mm; max-width:100%; }
figure.fig svg { max-width: 100%; height: auto; }
figcaption { font-family:'TeX Gyre Heros',sans-serif; font-size: 8.6pt; color:#5d6b82;
             margin-top: 2.4mm; text-align: left; line-height:1.4; }
figcaption .lab { color:#1f5fa8; font-weight:600; }
figure.tbl { margin: 5mm 0; break-inside: avoid; }
table.data { width: 100%; border-collapse: collapse; font-size: 9.3pt; }
table.data th { font-family:'TeX Gyre Heros',sans-serif; font-size: 8.4pt;
                letter-spacing:.08em; text-transform:uppercase; color:#1f5fa8;
                text-align:left; padding: 2.2mm 3mm; border-bottom:1.6px solid #1f5fa8; }
table.data td { padding: 2.1mm 3mm; border-bottom:1px solid #e6ebf2;
                vertical-align: top; }
table.data tbody tr:nth-child(even) { background:#f8fafc; }
table.deflist { border-collapse: collapse; margin: 3.4mm 0 4mm; font-size: 9.6pt;
                break-inside: avoid; }
table.deflist td { padding: 1.5mm 0; vertical-align: baseline; }
table.deflist .dk { font-family:'TeX Gyre Heros',sans-serif; font-weight:600;
                    color:#14243c; padding-right: 4mm; white-space: nowrap; }
table.deflist .dop { color:#1f5fa8; padding-right: 4mm; font-weight:600; }
table.deflist .dv { color:#46566d; }
"""


# ------------------------------------------------------------------ build one volume
def build(part):
    pn = part['no']
    motif = '<span class="arw">\u2192</span>'.join(
        f'<span class="chip">{esc(x)}</span>' for x in MOTIF[pn])
    ctx = Ctx()
    body = []

    # cover -------------------------------------------------------
    body.append(f'''
<section class="cover">
  <div class="lower"></div><div class="band"></div>
  <div class="inner">
    <div class="kicker">{esc(BOOK_TITLE)}</div>
    <h1>{esc(part['title'])}</h1>
    <div class="vol">{VOLNAME[pn]} of III</div>
    <div class="rule"></div>
    <div class="sub">{esc(part['subtitle'])}</div>
  </div>
  <div class="blurb">{esc(VOL_BLURB[pn])}</div>
  <div class="motif">{motif}</div>
  <div class="booktitle">{esc(BOOK_SUB)}</div>
  <div class="set">Part {ROMAN[pn]} / III</div>
</section>''')

    # collect chapter content first so TOC + LOF can be emitted before it
    chapters_html = []
    for ch in part['chapters']:
        ctx.chap = ch['no']
        ctx.fig = 0
        ctx.tab = 0
        cid = f'ch-{pn}-{ch["no"]}'
        secs = ''.join(
            f'<div><span>{ch["no"]}.{k}</span>&ensp;{esc(s["title"])}</div>'
            for k, s in enumerate(ch['sections'], 1))
        inner = [f'''<section class="chapter" id="{cid}">
  <header class="chapopen">
    <div class="cno">Chapter {ch['no']}</div>
    <h2>{esc(ch['title'])}</h2>
    <div class="crule"></div>
    <div class="clist">{secs}</div>
  </header>''']
        for k, s in enumerate(ch['sections'], 1):
            sid = f'sec-{pn}-{ch["no"]}-{k}'
            inner.append(f'<h3 class="sec" id="{sid}">'
                         f'<span class="n">{ch["no"]}.{k}</span>{esc(s["title"])}</h3>')
            inner.append(render_blocks(s['blocks'], ctx))
        inner.append('</section>')
        chapters_html.append((ch, ''.join(inner), list(ctx.figlist)))
        ctx.figlist = []

    # front matter -----------------------------------------------
    cards = ''.join(
        f'<div class="volcard{" me" if n == pn else ""}">'
        f'<div class="n">{VOLNAME[n]}</div><div class="t">{esc(t)}</div></div>'
        for n, t in VOL_LIST)
    intro_html = render_blocks(part['intro'], Ctx()) if part['intro'] else ''
    body.append(f'''
<section class="front">
  <h2 class="fm">About this volume</h2><div class="fmrule"></div>
  <div class="about">
  <p>{esc(VOL_BLURB[pn])}</p>
  <p>This is one of three volumes. Each descends a level further from the digits a
  human types toward the electromagnetic wave that eventually carries the speech.
  The volumes are meant to be read in order, but each is self-contained.</p>
  <div class="volcards">{cards}</div>
  <p>Diagrams are numbered by chapter. A list of figures follows the contents, so any
  diagram can be found directly.</p>
  </div>
</section>''')

    toc = ['<section class="front"><h2 class="fm">Contents</h2><div class="fmrule"></div>'
           '<ul class="toc">']
    for ch, _, _ in chapters_html:
        cid = f'ch-{pn}-{ch["no"]}'
        toc.append(f'<li><div class="ch"><span class="no">Ch {ch["no"]}</span>'
                   f'<span class="ti">{esc(ch["title"])}</span>'
                   f'<a class="pg" href="#{cid}"></a></div>')
        for k, s in enumerate(ch['sections'], 1):
            sid = f'sec-{pn}-{ch["no"]}-{k}'
            toc.append(f'<div class="sec"><span class="ti">{ch["no"]}.{k}&ensp;'
                       f'{esc(s["title"])}</span><span class="dots"></span>'
                       f'<a class="pg" href="#{sid}"></a></div>')
        toc.append('</li>')
    toc.append('<li><div class="ch"><span class="no">App A</span>'
               '<span class="ti">Glossary of Terms</span>'
               f'<a class="pg" href="#app-{pn}-a"></a></div></li>')
    toc.append('</ul></section>')
    body.append(''.join(toc))

    lof = ['<section class="front"><h2 class="fm">Figures</h2><div class="fmrule"></div>'
           '<ul class="lof">']
    for ch, _, figs in chapters_html:
        for num, cap, fid in figs:
            lof.append(f'<li><span class="no">Fig. {num}</span>'
                       f'<span class="ti">{esc(cap)}</span><span class="dots"></span>'
                       f'<a class="pg" href="#{fid}"></a></li>')
    lof.append('</ul></section>')
    body.append(''.join(lof))

    if intro_html:
        body.append(f'<section class="front" style="break-before:page">'
                    f'<h2 class="fm">Introduction</h2><div class="fmrule"></div>'
                    f'{intro_html}</section>')

    ghtml, gcount = gloss_render.build(part, f'app-{pn}-a')

    for _, hml, _ in chapters_html:
        body.append(hml)
    body.append(ghtml)

    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>{esc(part["title"])}</title><style>{CSS}</style></head>
<body>{''.join(body)}</body></html>'''


if __name__ == '__main__':
    from weasyprint import HTML
    import os
    os.makedirs('/mnt/user-data/outputs', exist_ok=True)
    names = {1: 'Part-1-Architecture-of-a-Phone-Number',
             2: 'Part-2-Anatomy-of-a-5G-Voice-Call',
             3: 'Part-3-Packet-Level-Telecommunications'}
    for part in doc:
        h = build(part)
        open(f'vol{part["no"]}.html', 'w').write(h)
        out = f'/mnt/user-data/outputs/{names[part["no"]]}.pdf'
        HTML(string=h, base_url='.').write_pdf(out)
        print('wrote', out)

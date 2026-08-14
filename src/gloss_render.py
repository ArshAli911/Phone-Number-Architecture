import re, html
import glossary


def esc(t):
    return html.escape(t, quote=False)


def part_text(part):
    out = []

    def walk(bs):
        for b in bs:
            if b['t'] in ('p', 'h3'):
                out.append(b['text'])
            elif b['t'] == 'ul':
                out.extend(b['items'])
            elif b['t'] == 'diagram':
                out.extend(b['lines'])
            elif b['t'] == 'table':
                for r in b['rows']:
                    out.extend(r)

    walk(part['intro'])
    for c in part['chapters']:
        for sec in c['sections']:
            out.append(sec['title'])
            walk(sec['blocks'])
    return ' \n '.join(out)


def entries(part):
    t = part_text(part)
    found = []
    for k, v in glossary.ACRONYMS.items():
        if re.search(r'(?<![A-Za-z0-9])' + re.escape(k) + r'(?![A-Za-z0-9])', t):
            found.append(v)
    for k, v in glossary.CONCEPTS.items():
        if re.search(re.escape(k), t, re.I):
            found.append(v)
    seen, uniq = set(), []
    for hw, exp, d in found:
        if hw in seen:
            continue
        seen.add(hw)
        uniq.append((hw, exp, d))

    def key(e):
        h = re.sub(r'[^A-Za-z0-9]', '', e[0]).upper()
        return (0 if h[:1].isdigit() else 1, h)

    return sorted(uniq, key=key)


NOTE = ('Every term below appears somewhere in this volume. Expansions are given where an '
        'acronym has one; the definitions describe the sense in which the term is used '
        'here rather than every sense it carries in the wider literature.')


def build(part, anchor):
    ent = entries(part)
    out = []
    out.append('<section class="chapter appendix" id="%s">' % anchor)
    out.append('<header class="chapopen">')
    out.append('<div class="cno">Appendix A</div>')
    out.append('<h2>Glossary of Terms</h2>')
    out.append('<div class="crule"></div>')
    out.append('<div class="gnote">%s</div>' % esc(NOTE))
    out.append('</header><div class="gloss">')
    cur = None
    for hw, exp, d in ent:
        h = re.sub(r'[^A-Za-z0-9]', '', hw).upper()
        grp = '0\u20139' if h[:1].isdigit() else h[:1]
        if grp != cur:
            cur = grp
            out.append('<div class="gletter">%s</div>' % esc(grp))
        e = '<span class="gexp">%s</span>' % esc(exp) if exp else ''
        out.append('<div class="gitem"><span class="ghw">%s</span>%s'
                   '<span class="gdef">%s</span></div>' % (esc(hw), e, esc(d)))
    out.append('</div></section>')
    return ''.join(out), len(ent)

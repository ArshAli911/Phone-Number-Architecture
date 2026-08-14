"""Export the README figures as SVG sources and display PNGs.

Run after model.py, from the src/ directory:

    python export_figures.py

Writes ../figures/svg/*.svg and ../figures/*.png.

PNG is what the README embeds: GitHub serves .svg from raw.githubusercontent.com as
text/plain with X-Content-Type-Options: nosniff, so a browser will not render it inside
an <img> tag. The SVGs are kept as the editable source.
"""
import json, os, re, subprocess, tempfile

import figures as figengine

# figure index in the generated sequence -> output basename
PICK = {
    2:   'fig-01-identifier-vs-address',
    0:   'fig-02-e164-structure',
    6:   'fig-03-identity-family',
    66:  'fig-04-switching-evolution',
    130: 'fig-05-call-sequence',
    140: 'fig-06-packet-stack',
    181: 'fig-07-encapsulation-gtpu',
    186: 'fig-08-loss-of-meaning',
    194: 'fig-09-intent-to-eardrum',
}

PAD = 8      # px of white margin baked into the PNG
SCALE = 2    # render at 2x so the images stay sharp on high-density screens
DPI = 96 * SCALE   # WeasyPrint treats px as CSS px (1/96in), so scale against 96

OUT_PNG = os.path.join('..', 'figures')
OUT_SVG = os.path.join('..', 'figures', 'svg')


def all_diagrams():
    doc = json.load(open('doc.json'))
    blocks = []

    def walk(bs):
        for b in bs:
            if b['t'] == 'diagram':
                blocks.append(b['lines'])

    for p in doc:
        walk(p['intro'])
        for c in p['chapters']:
            for s in c['sections']:
                walk(s['blocks'])
    return blocks


def main():
    os.makedirs(OUT_PNG, exist_ok=True)
    os.makedirs(OUT_SVG, exist_ok=True)

    from weasyprint import HTML
    from PIL import Image

    rendered = [figengine.make_figure(l) for l in all_diagrams()]

    for idx, name in sorted(PICK.items(), key=lambda kv: kv[1]):
        svg, kind, _cap = rendered[idx]
        if kind == 'inline':
            raise SystemExit(f'figure {idx} is inline, not a diagram')

        # opaque background so the figure stays legible in GitHub dark mode
        head = re.match(r'(<svg[^>]*>)', svg)
        svg = head.group(1) + '<rect width="100%" height="100%" fill="#ffffff"/>' \
            + svg[head.end():]

        svg_path = os.path.join(OUT_SVG, name + '.svg')
        with open(svg_path, 'w') as fh:
            fh.write(svg)

        w, h = map(int, re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
        W, H = w + 2 * PAD, h + 2 * PAD
        html = (
            f'<html><head><meta charset="utf-8"><style>'
            f'@page{{size:{W}px {H}px;margin:0}}'
            f'body{{margin:0;background:#fff}}'
            f'img{{display:block;margin:{PAD}px}}'
            f'</style></head><body>'
            f'<img src="{os.path.abspath(svg_path)}" width="{w}" height="{h}">'
            f'</body></html>')

        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, 'f.pdf')
            HTML(string=html, base_url='.').write_pdf(pdf)
            base = os.path.join(tmp, 'f')
            subprocess.run(['pdftoppm', '-png', '-r', str(DPI),
                            '-f', '1', '-l', '1', pdf, base], check=True)
            png_path = os.path.join(OUT_PNG, name + '.png')
            Image.open(base + '-1.png').convert('RGB').save(png_path, optimize=True)

        px = Image.open(png_path).size
        print(f'{name}  svg {w}x{h}  png {px[0]}x{px[1]}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Embed a draw.io model into an SVG -> editable .drawio.svg.
Usage: python3 embed_drawio.py VISIBLE.svg MODEL.mxfile OUT.drawio.svg
Stdlib only. Validates the result; exits non-zero on any problem.
"""
import re
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

SVG_NS = 'http://www.w3.org/2000/svg'


def attr_escape(model: str) -> str:
    """Escape one XML document for use as an XML attribute value."""
    # Drop characters XML 1.0 forbids (mirrors draw.io's mxUtils.zapGremlins).
    model = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', model)
    model = model.replace('\r\n', '\n').replace('\r', '\n')
    s = escape(model, {'"': '&quot;', "'": '&#39;'})
    # Attribute-value normalization turns literal whitespace into spaces.
    return s.replace('\n', '&#10;').replace('\t', '&#9;')


def embed(svg_text: str, model: str) -> str:
    # 1. The model must be a bare mxfile/mxGraphModel, no declaration/comments.
    model = model.strip()
    model = re.sub(r'^<\?xml[^>]*\?>\s*', '', model)
    model = re.sub(r'^(?:<!--.*?-->\s*)+', '', model, flags=re.S)
    if not model.startswith(('<mxfile ', '<mxGraphModel ')):
        raise ValueError('model must start with "<mxfile " or "<mxGraphModel "')

    # 2. Find the root <svg ...> start tag.
    m = re.search(r'<svg\b[^>]*>', svg_text, re.S)
    if not m:
        raise ValueError('no <svg> root element found')
    head = m.group(0)

    # 3. Replace any existing content attribute, ensure xmlns.
    head = re.sub(r'\s+content\s*=\s*"[^"]*"', '', head, flags=re.S)
    head = re.sub(r"\s+content\s*=\s*'[^']*'", '', head, flags=re.S)
    if 'xmlns=' not in head:
        head = head.replace('<svg', '<svg xmlns="' + SVG_NS + '"', 1)

    # 4. Insert the escaped model as content="..." before the closing '>'.
    head = head[:-1] + ' content="' + attr_escape(model) + '">'
    return svg_text[:m.start()] + head + svg_text[m.end():]


def _num(el, key: str, default=None):
    """First number in an attribute (handles '1280', '1280px', '14')."""
    raw = el.get(key)
    if raw is None:
        return default
    m = re.match(r'-?\d+(?:\.\d+)?', raw.strip())
    return float(m.group(0)) if m else default


def layout_warnings(root) -> list:
    """Measure the visible layer against drawio-svg-format.md proportions."""
    ns = '{' + SVG_NS + '}'
    vb = (root.get('viewBox') or '').replace(',', ' ').split()
    if len(vb) == 4:
        W, H = float(vb[2]), float(vb[3])
    else:
        W, H = _num(root, 'width'), _num(root, 'height')
    if not W or not H:
        return ['cannot read a viewBox/width/height from the root <svg>']

    spans, fonts, box_heights = [], [], []

    def walk(el, is_logo):
        is_logo = is_logo or (
            el.tag == ns + 'g' and 'logo' in (el.get('id') or '').lower())
        if not is_logo:
            tag = el.tag.replace(ns, '')
            if tag == 'rect':
                x, y = _num(el, 'x'), _num(el, 'y')
                w, h = _num(el, 'width'), _num(el, 'height')
                if None not in (x, y, w, h) and not (w == W and h == H):
                    spans.append((x, y, x + w, y + h))
                    if el.get('rx'):
                        box_heights.append(h)
            elif tag == 'image':
                x, y = _num(el, 'x'), _num(el, 'y')
                w, h = _num(el, 'width'), _num(el, 'height')
                if None not in (x, y, w, h):
                    spans.append((x, y, x + w, y + h))
            elif tag == 'text':
                x, y = _num(el, 'x'), _num(el, 'y')
                fs = _num(el, 'font-size')
                if fs is None:  # some authors put it in style="font-size:14px"
                    m = re.search(r'font-size\s*:\s*([\d.]+)', el.get('style') or '')
                    fs = float(m.group(1)) if m else 14.0
                fonts.append(fs)
                if x is not None and y is not None:
                    width = 0.55 * fs * len(''.join(el.itertext()))
                    spans.append((x, y - fs, x + width, y))
        for child in el:
            walk(child, is_logo)

    walk(root, False)
    if not spans:
        return ['no visible geometry (rects/image/text) found outside the logo']

    x0 = min(s[0] for s in spans); y0 = min(s[1] for s in spans)
    x1 = max(s[2] for s in spans); y1 = max(s[3] for s in spans)
    fill_w, fill_h = (x1 - x0) / W, (y1 - y0) / H
    out = []
    if W < 1100 or W > 1450:
        out.append(f'canvas {W:.0f}px wide is outside the 1120-1440 band '
                   f'(default 1280) - size the canvas to the content')
    if fill_w < 0.80:
        out.append(f'picture fills only {fill_w:.0%} of canvas width '
                   f'(want >= 85%) - shrink the canvas or spread the flow')
    if fill_h < 0.65:
        out.append(f'picture fills only {fill_h:.0%} of canvas height '
                   f'(want >= 70%) - drop unused rows/spacing and shrink '
                   f'the canvas height')
    if H - y1 > 130:
        out.append(f'{H - y1:.0f}px blank band below the lowest element '
                   f'(want 32-110px, logo only) - reduce canvas height')
    if fonts and min(fonts) < 12:
        out.append(f'font-size {min(fonts):.0f} is below the 12px floor; '
                   f'type smaller than this is unreadable at README width')
    if box_heights and min(box_heights) < 60:
        out.append(f'a component box is {min(box_heights):.0f}px tall '
                   f'(want 76-100) - let text drive the box size')
    if box_heights and max(box_heights) > 120:
        out.append(f'a component box is {max(box_heights):.0f}px tall '
                   f'(want 76-100) - size boxes to their text, not the canvas')
    return out


def validate(path: str, model: str) -> None:
    root = ET.parse(path).getroot()          # whole file is well-formed XML
    if root.tag != '{' + SVG_NS + '}svg':
        raise ValueError('root element is not SVG: ' + root.tag)
    content = root.get('content')
    if content is None:
        raise ValueError('missing content attribute')
    if not content.startswith(('<mxfile ', '<mxGraphModel ')):
        raise ValueError('content must start immediately with <mxfile ...')
    inner = ET.fromstring(content)           # embedded model is well-formed
    if content != model:                     # exact round-trip (newlines decoded)
        raise ValueError('content does not round-trip to the input model')
    cells = inner.findall('.//mxCell')
    if not cells:
        raise ValueError('model has no mxCell elements')
    print(f'OK {path}: root=svg, content={len(content)} chars, mxCells={len(cells)}')
    warns = layout_warnings(root)
    for w in warns:
        print('LAYOUT: ' + w)
    if not warns:
        print('LAYOUT: ok (proportions)')


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__.strip().splitlines()[1], file=sys.stderr)
        return 2
    svg_path, model_path, out_path = sys.argv[1:]
    svg_text = open(svg_path, encoding='utf-8').read()
    model = open(model_path, encoding='utf-8').read()
    model = re.sub(r'^<\?xml[^>]*\?>\s*', '', model.strip())
    model = re.sub(r'^(?:<!--.*?-->\s*)+', '', model, flags=re.S).strip()
    open(out_path, 'w', encoding='utf-8').write(embed(svg_text, model))
    validate(out_path, model)
    return 0


if __name__ == '__main__':
    sys.exit(main())

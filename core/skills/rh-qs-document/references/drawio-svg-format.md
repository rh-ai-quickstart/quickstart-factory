# draw.io-editable SVG — the generated architecture diagram's file format

WHAT the diagram shows is decided by `template-structure.md`
(Architecture diagrams) and `evidence-hunting.md` §8 (content
selection). This file says HOW the file is built: one hand-authored
`docs/images/architecture-overview.drawio.svg` that GitHub renders as
a normal image and draw.io (web, desktop, VS Code extension) reopens
editable. It is draw.io's own "editable SVG" convention: the diagram
model lives XML-escaped in the root `<svg>`'s `content` attribute;
draw.io reads that attribute and ignores the visible shapes; GitHub
renders the visible shapes and ignores the attribute.

Hand-author only: never launch the drawio app, never fetch stencils or
URLs, never render — plain XML text plus the script below, fully
offline.

## One file, two representations

- **Visible layer** — a normal standalone SVG: white background rect,
  dashed cluster boundary, rounded-rect boxes (bold repo name + optional
  one-line feature sub-label) colored by grouping (next section),
  orthogonal arrows with an arrowhead marker and small grey labels,
  external systems outside the boundary, inside the right margin,
  Red Hat logo at the bottom.
- **Model layer** — `<mxfile>` → `<diagram>` → `<mxGraphModel>` →
  `<root>` of `mxCell` vertices/edges, XML-escaped into `content`.

They are independent: anything visible-only (including the logo) is
deleted the first time a human opens and saves the file in draw.io, and
model-only content never renders on GitHub. Build both from ONE cell
list with identical coordinates: every visible `<g id="box-X">` maps
1:1 to an `<mxCell id="X">`; a vertex's `mxGeometry x/y/width/height`
equals its rect's coordinates; an edge's `exitX/exitY` (source) and
`entryX/entryY` (target) are the fractional anchors of its visible
path endpoints on the box borders.

## Color encodes grouping — nothing else

Box color maps 1:1 to the content tier from `evidence-hunting.md` §8,
so the grouping reads at a glance. Same tier, same color, everywhere in
the picture; both layers carry it (visible `fill`/`stroke` AND the
mxCell `fillColor=`/`strokeColor=`).

| Group (tier) | Fill | Stroke | Weight |
|---|---|---|---|
| Application solution core — headline-feature surfaces and engines | `#FCE8E6` | `#EE0000` (Red Hat red) | stroke-width 2 — the strongest boxes on the canvas |
| Architecture-bearing tools the feature journeys cross | `#E7F1FA` | `#0066CC` | 1.5 |
| External systems (outside the cluster, or platform-provided at the periphery) | `#F2F2F2` | `#6A6E73`, dashed `6 4` | 1.5 |
| Optional / detached alternatives (max two, never on a main arrow) | `#FDF3D7` | `#F0AB00`, dashed | 1.5 |
| Cluster boundary frame | none | `#6A6E73`, dashed `10 8` | 1.5, grey italic label |
| Background, arrows, labels | white `#ffffff` | arrows `#4d4d4d`, labels `#5e5e5e`, titles `#151515` | — |

Rules: color is rendering, not evidence — it adds no fact (Invariant 1
is untouched) and encodes nothing beyond the tier (never status,
health, or vendor; the core's red is the Red Hat brand accent, not an
alert). Fills are light tints on the white background so the diagram
prints and survives dark-mode viewers. The Red Hat logo keeps its own
brand colors, unchanged.

## Proportions — one scale for the whole picture

Every element is sized against the canvas, and the canvas against the
content. Two failure modes read at a glance: a sparse picture afloat on
an oversized canvas (GitHub shrinks the whole SVG to README width, so
boxes and type land illegibly small), or boxes inflated until the flow
has no air. Size the canvas from the drawn content, then hold
everything to one scale.

- **Canvas from the content.** Lay the flow out at natural size first,
  then set the canvas to picture + margins. Default 1280×700; 1120–1440
  wide when the flow needs it, height following the rows. Never a fixed
  oversized canvas.
- **Fill it.** The drawn picture (cluster frame + boxes + external
  boxes; logo excluded) spans ≥ 85% of the canvas width and ≥ 70% of
  its height. The lowest drawn element ends 32–110px above the bottom
  edge — that band is the logo's. No blank strip below the flow, no
  empty row of boxes.
- **Margins.** 48px to the canvas edge; external-system boxes end
  32–60px inside the right edge, never jammed at ~20px; the cluster
  frame keeps 40px padding around what it holds.
- **Boxes.** 180–260 wide × 76–100 tall — a bold title plus one
  sub-label with 16px side padding. All boxes in a row share one
  height; 60–90px gutters; rows and columns aligned to a grid.
- **Type at 1280 wide.** Box title 18–20 bold, sub-label 14, arrow
  label 13, cluster label 14 italic. **No text below 12px** — below
  that, GitHub's README-width rendering is unreadable. On a wider
  canvas scale every type size by `canvas_width / 1280`; never shrink
  type to fit — shorten the label, widen the box, or drop the box.
- **Logo.** 96×73 (7.5% of canvas width) at the bottom-right corner,
  32px from the right edge, ~12px from the bottom.

`embed_drawio.py` measures all of this and prints a `LAYOUT:` line for
every band it finds violated. Each one is a defect to fix by resizing
the canvas or the elements — never a warning to ignore.

## Model validity rules (draw.io enforces these)

- `mxCell id="0"` and `id="1" parent="0"` must exist.
- Every vertex has `<mxGeometry x y width height as="geometry"/>`;
  every edge references existing `source`/`target` ids and has
  `<mxGeometry relative="1" as="geometry"/>`.
- Ids are unique; every `parent` references an existing id.
- `style` is `key=value;` pairs — a value must never contain a literal
  semicolon (why image data URIs use `data:image/svg+xml,<payload>`
  with no `;base64` marker).
- No XML comments inside the model; no XML declaration inside
  `content`; the model is uncompressed; `content` starts immediately
  with `<mxfile ` — leading whitespace makes draw.io mis-detect the
  encoding and fail.
- `pageWidth`/`pageHeight` equal the visible `viewBox` size.

## Building the file — never hand-escape

Write two scratch files (under `/tmp`, never inside the repo): the
visible SVG WITHOUT a `content` attribute, and the model as a
standalone `<mxfile>` text file. Then fuse and validate:

```bash
python3 <skill-dir>/references/embed_drawio.py /tmp/visible.svg /tmp/model.mxfile \
        docs/images/architecture-overview.drawio.svg
```

`<skill-dir>` is the directory SKILL.md lives in. The script
XML-entity-escapes the model into the root svg's `content` attribute
(`&` `<` `>` `"` `'` newlines tabs, in that order of concern) and
validates: the whole file parses, the root is an SVG, `content`
unescapes to a parseable `<mxfile>` that round-trips exactly to the
input, and mxCells exist. A non-zero exit is a defect to fix, never to
bypass. Only the final `.drawio.svg` lands under the README's
`docs/images/`.

## The Red Hat logo — bottom of the canvas, in BOTH layers

Visible: both `<path>` elements from `references/redhat-logo.svg`
verbatim inside `<g transform="translate(1152,616) scale(0.5)">` on the
default 1280×700 canvas (~96×73 px; 32px right margin, ~12px bottom —
rescale the translate for other canvas sizes). Model: an image cell, so
draw.io editing keeps it:

```xml
<mxCell id="redhat-logo" value="" vertex="1" parent="1"
        style="shape=image;image=data:image/svg+xml,BASE64;">
  <mxGeometry x="1152" y="616" width="96" height="73" as="geometry"/>
</mxCell>
```

`BASE64` is the output of `base64 -w0 <skill-dir>/references/redhat-logo.svg`
(a URL-encoded copy of the SVG is equivalent; either way the style
value must contain no semicolon). A visible-only logo is lost on the
first draw.io save.

## Referencing it from the README

Markdown image syntax — never an HTML `<img>` tag, which the template
checker's image rules do not see:

```markdown
![<one-sentence alt text following the main journey>](docs/images/architecture-overview.drawio.svg)
```

## Skeletons

Visible layer (excerpt):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="700"
     viewBox="0 0 1280 700" font-family="Red Hat Text, Helvetica, sans-serif"
     content="&lt;mxfile ...&gt;...entire model, XML-escaped...&lt;/mxfile&gt;">
  <title>one-line alt text for the diagram</title>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#4d4d4d"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="1280" height="700" fill="#ffffff"/>
  <g id="cluster-openshift">
    <rect x="48" y="80" width="980" height="520" fill="none"
          stroke="#a3a3a3" stroke-width="1.5" stroke-dasharray="10 8"/>
    <text x="72" y="114" font-size="14" font-style="italic"
          fill="#666666">OpenShift cluster</text>
  </g>
  <!-- one <g id="edge-eN"> per main-flow arrow, drawn before the boxes:
       <path d="M 298,335 H 370" fill="none" stroke="#4d4d4d"
             stroke-width="1.5" marker-end="url(#arrow)"/>
       + a small grey label <text font-size="13" fill="#5e5e5e">chat</text> -->
  <!-- one <g id="box-<id>"> per component box (id = the mxCell id),
       on a grid: rows at y=160/290/420 of height 90, columns 88/370/660:
       <rect x="88" y="290" width="210" height="90" rx="8"
             fill/stroke per the tier palette above
             (core #FCE8E6/#EE0000 w2, tool #E7F1FA/#0066CC,
              external #F2F2F2/#6A6E73 dashed)/>
       <text x="104" y="332" font-size="18" font-weight="bold"
             fill="#151515">Web UI</text>
       <text x="104" y="356" font-size="14" fill="#5e5e5e">one-line feature sub-label</text>
       external-system boxes sit outside the cluster boundary, 32-60px
       inside the right canvas edge; optional/detached alternatives sit
       off the main flow, dashed gold #FDF3D7/#F0AB00 -->
  <g id="box-redhat-logo" transform="translate(1152,616) scale(0.5)">
    <!-- the two <path> elements from references/redhat-logo.svg, verbatim -->
  </g>
</svg>
```

Model layer (pretty-printed for reading; embedded escaped):

```xml
<mxfile host="app.diagrams.net" type="device">
  <diagram id="architecture-overview" name="architecture-overview">
    <mxGraphModel grid="0" page="1" pageScale="1"
                  pageWidth="1280" pageHeight="700" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <mxCell id="openshift" value="OpenShift cluster"
                style="rounded=0;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 8;fillColor=none;strokeColor=#a3a3a3;verticalAlign=top;align=left;spacingLeft=12;fontSize=14;fontStyle=2;fontColor=#666666;"
                vertex="1" parent="1">
          <mxGeometry x="48" y="80" width="980" height="520" as="geometry"/>
        </mxCell>
        <!-- one vertex per visible box: value = "<b>Title</b><br>
             <font ...>sub-label</font>", mxGeometry = the visible rect,
             fillColor=/strokeColor= mirrored from the tier palette -->
        <mxCell id="webui"
                value="&lt;b&gt;Web UI&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size:14px&quot; color=&quot;#5e5e5e&quot;&gt;PatternFly chat interface&lt;/font&gt;"
                style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FCE8E6;strokeColor=#EE0000;arcSize=6;fontSize=18;fontColor=#151515;"
                vertex="1" parent="1">
          <mxGeometry x="88" y="290" width="210" height="90" as="geometry"/>
        </mxCell>
        <!-- one edge per visible arrow: exitX/exitY = fractional anchor
             on the source box border, entryX/entryY on the target -->
        <mxCell id="e2" value="chat"
                style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;fontSize=12;fontColor=#5e5e5e;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                edge="1" parent="1" source="webui" target="agent">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        <!-- the logo as an image cell so draw.io editing keeps it -->
        <mxCell id="redhat-logo" value="" vertex="1" parent="1"
                style="shape=image;image=data:image/svg+xml,&lt;logo data URI&gt;">
          <mxGeometry x="1152" y="616" width="96" height="73" as="geometry"/>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## How it should look — in words

There is deliberately NO example file: a worked example's fictional
components bias content selection. Build the picture from this
description and the target repo's ledgers only.

Picture a 1280×700 white canvas, sized to the flow rather than fixed —
the frame fills most of its width and height, with only margin around
it. A dashed grey frame near the edges
carries the cluster label (the repo's own platform name, grey italic).
Slightly left of center sits the application solution core: two to
four red-tinted boxes with the strongest strokes on the canvas —
first the surface the user touches, then the engine that does the
work, left to right in the user's journey order — each with its bold
repo name and at most one repo-verbatim feature sub-label. A step
lighter, around and right of the core, blue-tinted boxes hold the
architecture-bearing tools the journey actually crosses — only those
the arrows touch. At the right edge, outside the frame, one or two
grey dashed boxes mark the external systems the journey starts from
or ends at. A first-class alternative, when it deserves mention, is
one gold dashed box floating detached off the flow. Orthogonal
dark-grey arrows run left to right along the main journey, each
labeled at most with a repo-stated protocol or topic, in small grey
text. The Red Hat logo sits alone at the bottom-right, outside the
flow. White space is part of the design: ONLY the main features earn
space — when in doubt, cut a box, never shrink the text.

## Component logos — optional, repo-shipped only

To make the picture visually stronger, a component's box may carry
that component's logo INSTEAD of its bold title — but only when the
repository itself ships that logo. Search the repo's image and asset
dirs (`docs/images/`, `assets/`, `static/`, `public/`, UI asset
folders) for an image file whose name — or the doc that references
it — identifies it as that component's logo.

- The component name must stay readable: in the logo itself, or as
  the box label beside/below it. A logo never replaces the tier
  color, stroke, or the sub-label semantics — grouping stays
  color-coded.
- Inline it as a data URI in BOTH layers, exactly like the Red Hat
  logo: an SVG logo's markup inlined verbatim; a PNG logo embedded
  as `data:image/png;base64,...` produced by `base64 -w0 <file>`
  (never open the binary — encoding it via Bash is enough) in a
  visible `<image>` and an mxCell `shape=image` style. The style
  value must still contain no semicolon.
- NEVER fetch, invent, or recreate a logo from memory or general
  knowledge. No logo in the repo → plain tier-colored box, which is
  fully correct.
- The Red Hat logo stays the bottom brand mark only, never a
  component; logos appear only for components the repo deploys or
  names as external systems.

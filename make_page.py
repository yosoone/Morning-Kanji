"""Build a one-page reMarkable 2 morning page from a day's JSON file.

Usage: python3 make_page.py days/2026-11-03-iki.json out.pdf
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
E = html.escape

# reMarkable 2: 1404 x 1872 px at 226 dpi
PAGE_W, PAGE_H = "157.8mm", "210.4mm"
FOOTER_TOP = "196.5mm"  # where the sources line starts
MARGIN = {"T": "9mm", "B": "15mm", "L": "18mm", "R": "12mm"}  # wider left for the toolbar

# Line weights in millimetres, so they look the same in every box size
EDGE_MM = 0.12    # box outlines
GUIDE_MM = 0.08   # dashed centre guides
INK = "#222"      # outlines and ruled lines
GUIDE = "#999"
RULE = "#aaa"     # soft grey writing lines
GHOST = "#bbb"    # tracing strokes
DONE = "#888"     # earlier strokes in the stroke-order row


def load_strokes(code):
    svg = (HERE / "kanjivg" / f"{code}.svg").read_text(encoding="utf-8")
    return re.findall(rf'<path id="kvg:{code}-s\d+"[^>]*\sd="([^"]+)"', svg)


def box(inner, mm):
    """A square writing box with thin outline and dashed centre guides."""
    u = 113 / mm  # viewBox units per mm
    edge, guide = EDGE_MM * u, GUIDE_MM * u
    dash = f"{1.2 * u:.2f} {1.2 * u:.2f}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{mm}mm" height="{mm}mm" viewBox="-2 -2 113 113">'
        f'<line x1="54.5" y1="0" x2="54.5" y2="109" stroke="{GUIDE}" stroke-width="{guide:.2f}" stroke-dasharray="{dash}"/>'
        f'<line x1="0" y1="54.5" x2="109" y2="54.5" stroke="{GUIDE}" stroke-width="{guide:.2f}" stroke-dasharray="{dash}"/>'
        f'<rect x="0" y="0" width="109" height="109" fill="none" stroke="{INK}" stroke-width="{edge:.2f}"/>'
        f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">{inner}</g></svg>'
    )


def paths(strokes, idx, colour, width):
    return "".join(f'<path d="{strokes[i]}" stroke="{colour}" stroke-width="{width}"/>' for i in idx)


LINK = re.compile(r"\b((?:[a-z0-9-]+\.)+(?:org|net|one|com|jp))\b")


CC = re.compile(r"CC BY-SA ([34])\.0")


def linkify(text):
    """Turn bare domain names and licence names into clickable links in the PDF.
    CC BY-SA asks for the licence's web address with each copy; the link carries it."""
    text = LINK.sub(r'<a href="https://\1" style="color:#222;text-decoration:none;">\1</a>', text)
    return CC.sub(r'<a href="https://creativecommons.org/licenses/by-sa/\1.0/" '
                  r'style="color:#222;text-decoration:none;">CC BY-SA \1.0</a>', text)


def sup(n):
    return f"<sup>{n}</sup>" if n else ""


def build_html(day, rows):
    s = load_strokes(day["kanjivg"])
    n = len(s)
    assert n == day["strokes"], f"stroke data has {n} strokes, day file says {day['strokes']}"

    # Composition: part + part = whole
    comp_mm = 21
    cells, caps = [], []
    for i, p in enumerate(day["parts"]):
        a, b = p["strokes"]
        cells.append(box(paths(s, range(a - 1, b), "#000", 3.4), comp_mm))
        caps.append(f'<span class="jp">{E(p["kana"])}</span> {E(p["romaji"])}<br>{E(p["meaning"])}')
        if i < len(day["parts"]) - 1:
            cells.append("+"); caps.append("")
    cells.append("="); caps.append("")
    cells.append(box(paths(s, range(n), "#000", 3.4), comp_mm))
    caps.append(f'<span class="jp">{E(day.get("kana", day["kun"]["kana"]))}</span> {E(day["romaji"])}<br>{E(day["meaning"])}')
    comp = '<table class="comp"><tr>' + "".join(
        f'<td class="op">{c}</td>' if c in "+=" else f"<td>{c}</td>" for c in cells
    ) + "</tr><tr>" + "".join(f'<td class="cap">{c}</td>' for c in caps) + "</tr></table>"

    # Stroke order and tracing rows share one grid
    cell = 19
    per_row = 5
    order_cells = [
        f"<td>{box(paths(s, range(k - 1), DONE, 3.4) + paths(s, [k - 1], '#000', 4.4), cell)}</td>"
        for k in range(1, n + 1)
    ]
    order_rows = [order_cells[i:i + per_row] for i in range(0, n, per_row)]
    order = '<div style="height:1.5mm"></div>'.join(
        '<table class="grid"><tr>' + "".join(r) + "</tr></table>" for r in order_rows
    )
    trace = "".join(
        f"<td>{box(paths(s, range(n), GHOST, 3.4) if k < 2 else '', cell)}</td>" for k in range(per_row)
    )

    words = day.get("words", [])
    w = [
        f'<span class="jp">{E(x["word"])}</span> <span class="jp kana">{E(x["kana"])}</span> '
        f'{E(x["romaji"])}, {E(x["meaning"])}{sup(x.get("fn"))}'
        for x in words
    ]
    note = day.get("note")
    if note:
        w.append(f'{E(note["text"])}{sup(note.get("fn"))}')
    half = (len(w) + 1) // 2
    words_html = (" &nbsp;·&nbsp; ".join(w[:half]) + "<br>" + " &nbsp;·&nbsp; ".join(w[half:])) if w else ""

    c = day.get("classic")
    classic = ""
    if c:
        classic = (
            f'<div class="lab">{E(c["label"])}</div>'
            f'<div class="jp classic">{E(c["text"])}</div>'
            f'<div class="body"><span class="jp kana">{E(c["kana"])}</span> {E(c["romaji"])}{sup(c.get("kana_fn"))}'
            f' &nbsp;·&nbsp; “{E(c["translation"])}”{sup(c.get("fn"))}</div>'
        )

    srcs = " &nbsp;".join(f"{i}. {linkify(E(t))}" for i, t in enumerate(day["sources"], 1))

    css = f"""
    * {{ margin:0; padding:0; }}
    body {{ font-family:'Noto Sans CJK JP',sans-serif; color:#111; font-size:13pt; line-height:1.45; }}
    table {{ border-collapse:collapse; }} td {{ vertical-align:top; }}
    .jp {{ font-family:'Noto Sans CJK JP',sans-serif; }}
    .kana {{ color:#222; }}
    sup {{ font-size:8pt; line-height:0; }}
    .big {{ font-size:82pt; line-height:1; }}
    .name {{ font-size:20pt; font-weight:bold; }}
    .name span {{ font-size:14pt; font-weight:normal; color:#444; }}
    .comp td {{ padding:0; }}
    .comp .op {{ font-size:17pt; color:#555; padding:0 1.6mm; vertical-align:middle; }}
    .comp .cap {{ font-size:11pt; color:#222; line-height:1.3; padding-top:1mm; }}
    .lab {{ font-size:9.5pt; font-weight:bold; letter-spacing:1.4px; color:#444; text-transform:uppercase; margin:5mm 0 2mm 0; }}
    .meta {{ margin-top:2.5mm; color:#222; }}
    .grid td {{ padding:0 1.5mm 0 0; }}
    .grid td:last-child {{ padding-right:0; }}
    .body {{ color:#111; }}
    .classic {{ font-size:18pt; letter-spacing:2px; line-height:1.3; }}
    .prompt {{ font-size:17pt; font-weight:500; }}
    .row {{ border-bottom:0.35pt solid {RULE}; height:11mm; }}
    .fn {{ font-size:9.5pt; color:#222; line-height:1.4; }}
    """

    body = f"""
    <table><tr>
      <td style="width:42mm"><div class="big jp">{E(day["kanji"])}</div>
        <div class="name">{E(day["romaji"])} <span>{E(day["meaning"])}</span></div></td>
      <td style="padding-top:1mm">{comp}</td>
    </tr></table>
    <div class="meta"><span class="jp kana">{E(day["kun"]["kana"])}</span> {E(day["kun"]["romaji"])} (kun) &nbsp;·&nbsp;
      <span class="jp kana">{E(day["on"]["kana"])}</span> {E(day["on"]["romaji"])} (on) &nbsp;·&nbsp;
      {day["strokes"]} strokes &nbsp;·&nbsp; grade {day["grade"]}{sup(day.get("info_fn"))}</div>

    <div class="lab">Stroke order · trace</div>
    {order}
    <div style="height:1.5mm"></div>
    <table class="grid"><tr>{trace}</tr></table>

    {f'<div class="body" style="margin-top:3mm">{words_html}</div>' if words_html else ''}
    {classic}

    <div class="lab">Write a River text</div>
    <div class="prompt">{E(day["prompt"])}</div>
    {'<div class="row"></div>' * rows}
    """
    page = f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"
    footer = (
        "<!doctype html><html><head><meta charset='utf-8'><style>"
        "body{margin:0;font-family:'Noto Sans CJK JP',sans-serif;font-size:9.5pt;color:#222;line-height:1.4;}"
        f"</style></head><body><b>Sources</b> &nbsp;{srcs} &nbsp;·&nbsp; {linkify(E(day['credit']))}</body></html>"
    )
    return page, footer


def render(day, rows, out):
    tmp, foot = HERE / ".page.html", HERE / ".footer.html"
    page, footer = build_html(day, rows)
    tmp.write_text(page, encoding="utf-8")
    foot.write_text(footer, encoding="utf-8")
    subprocess.run(
        ["wkhtmltopdf", "-q", "--page-width", PAGE_W, "--page-height", PAGE_H,
         "-T", MARGIN["T"], "-B", MARGIN["B"], "-L", MARGIN["L"], "-R", MARGIN["R"],
         "--dpi", "226", "--title", f'{day["kanji"]} {day["romaji"]} · {day["date"]}',
         str(tmp), str(out)],
        stderr=subprocess.DEVNULL,
    )
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    if pages == 1:
        add_footer(foot, out, f'{day["kanji"]} {day["romaji"]} · {day["date"]}')
    return pages


def add_footer(foot_html, out, title):
    """Render the sources line near the page bottom and lay it over the page."""
    from pypdf import PdfReader, PdfWriter
    foot_pdf = HERE / ".footer.pdf"
    subprocess.run(
        ["wkhtmltopdf", "-q", "--page-width", PAGE_W, "--page-height", PAGE_H,
         "-T", FOOTER_TOP, "-B", "0mm", "-L", MARGIN["L"], "-R", MARGIN["R"], "--dpi", "226",
         str(foot_html), str(foot_pdf)],
        stderr=subprocess.DEVNULL,
    )
    w = PdfWriter()
    page = w.add_page(PdfReader(str(out)).pages[0])
    foot = PdfReader(str(foot_pdf)).pages[0]
    page.merge_page(foot)
    # merge_page also carries over the footer's links
    w.add_metadata({"/Title": title})
    with open(out, "wb") as f:
        w.write(f)


def main():
    day = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    for rows in range(16, 3, -1):  # as many writing lines as fit on one page
        if render(day, rows, out) == 1:
            print(f"{out}: one page, {rows} writing lines")
            return
    sys.exit("content does not fit on one page")


if __name__ == "__main__":
    main()

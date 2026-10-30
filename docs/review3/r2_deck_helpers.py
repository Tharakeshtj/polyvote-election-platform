"""Update PolyVote_Ppt (Review 1) into the Review 2 deck: edit existing slides, rebuild DFD/ER, add 11 slides, add speaker notes."""
import copy, json, os, re, sys
from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

SRC, OUT, SCR, ER_PNG = sys.argv[1:5]  # source pptx, output pptx, screenshots dir, ER png
NAVY, INK, MUTED = RGBColor(0x1B, 0x2A, 0x55), RGBColor(0x35, 0x3B, 0x4A), RGBColor(0x66, 0x6A, 0x78)
LAV, CHIP, BORDER, WHITE = RGBColor(0xF1, 0xF0, 0xF6), RGBColor(0xD8, 0xDF, 0xF3), RGBColor(0xD9, 0xD9, 0xE4), RGBColor(255, 255, 255)
GREEN, RED, AMBER = RGBColor(0x1A, 0x7F, 0x37), RGBColor(0xC0, 0x39, 0x2B), RGBColor(0x9A, 0x67, 0x00)
FONT = 'Inter'
FOOT = 'BACSE202 – Database Systems | Review 2 | Fall Semester 2026 · Slide {n}'

prs = Presentation(SRC)
slides = list(prs.slides)  # original order, 0-based
LAYOUT = slides[1].slide_layout

# ------------------------------------------------------------------ helpers
def para_fmt(p, size, color, bold, italic=False, align=PP_ALIGN.LEFT, after=0, font=FONT):
    p.alignment = align
    p.space_after = Pt(after)
    return dict(size=size, color=color, bold=bold, italic=italic, font=font)

def add_runs(p, parts, base):
    if isinstance(parts, str):
        parts = [(parts, {})]
    for text, o in parts:
        r = p.add_run(); r.text = text
        f = r.font; f.name = o.get('font', base['font']); f.size = Pt(o.get('size', base['size']))
        f.bold = o.get('bold', base['bold']); f.italic = o.get('italic', base['italic'])
        f.color.rgb = o.get('color', base['color'])

def tb(slide, x, y, w, h, paras, size=12, color=INK, bold=False, italic=False, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, after=0, name=None, shape=None, line_spacing=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: box.name = name
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(paras, str) or (paras and isinstance(paras[0], tuple)):
        paras = [paras]
    for i, parts in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        base = para_fmt(p, size, color, bold, italic, align, after)
        if line_spacing: p.line_spacing = line_spacing
        add_runs(p, parts, base)
    return box

def shape(slide, x, y, w, h, fill=None, line=None, lw=1.0, rounded=True, radius=0.07, dash=False, name=None):
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded: sp.adjustments[0] = radius
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None: sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
        if dash:
            ln = sp.line._get_or_add_ln(); d = etree.SubElement(ln, qn('a:prstDash')); d.set('val', 'dash')
    sp.shadow.inherit = False
    if name: sp.name = name
    return sp

def label_shape(slide, x, y, w, h, text, size=10, color=INK, fill=None, line=None, lw=1.0, bold=False, align=PP_ALIGN.CENTER,
                radius=0.1, dash=False, rounded=True):
    sp = shape(slide, x, y, w, h, fill, line, lw, rounded, radius, dash)
    tf = sp.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Inches(0.06); tf.margin_top = tf.margin_bottom = Inches(0.02)
    paras = text if isinstance(text, list) and text and isinstance(text[0], list) else [text]
    for i, parts in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        base = para_fmt(p, size, color, bold, False, align)
        add_runs(p, parts, base)
    return sp

def chip(slide, x, y, text, w=None):
    w = w or (0.34 + 0.105 * len(text))
    return label_shape(slide, x, y, w, 0.26, text, size=10, color=NAVY, fill=CHIP, bold=True, radius=0.15)

def arrow(slide, x1, y1, x2, y2, color=NAVY, lw=1.5, dash=False, both=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color; c.line.width = Pt(lw)
    ln = c.line._get_or_add_ln()
    if dash:
        d = etree.SubElement(ln, qn('a:prstDash')); d.set('val', 'dash')
    if both:
        h = etree.SubElement(ln, qn('a:headEnd')); h.set('type', 'triangle')
    t = etree.SubElement(ln, qn('a:tailEnd')); t.set('type', 'triangle')
    return c

def tag(slide, x, y, w, text, color=INK, fill=RGBColor(0xEC, 0xEC, 0xF3), size=8.5, align=PP_ALIGN.CENTER):
    return label_shape(slide, x, y, w, 0.2, text, size=size, color=color, fill=fill, align=align, radius=0.2)

def frame(slide, kicker, title, n):
    shape(slide, 8.7, 5.25, 1.3, 0.375, fill=WHITE, rounded=False, name='BadgeCover')
    tb(slide, 0.5, 0.5, 9.0, 0.16, kicker, size=9.5, color=NAVY, bold=True, name='Kicker')
    tb(slide, 0.5, 0.73, 9.0, 0.36, title, size=22, color=NAVY, bold=True, name='Title')
    tb(slide, 0.5, 5.36, 8.0, 0.18, FOOT.format(n=n), size=9.5, color=MUTED, name='Footer')

def card(slide, x, y, w, h, fill=WHITE, lw=2.0, radius=0.06):
    return shape(slide, x, y, w, h, fill=fill, line=NAVY, lw=lw, radius=radius)

def pic(slide, name, x, y, w=None, h=None, border=True):
    p = slide.shapes.add_picture(os.path.join(SCR, name), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if border: p.line.color.rgb = BORDER; p.line.width = Pt(1)
    return p

def new_slide():
    s = prs.slides.add_slide(LAYOUT)
    for ph in list(s.placeholders): ph._element.getparent().remove(ph._element)
    return s

def clear(slide, keep=()):
    for sh in list(slide.shapes):
        if sh.name not in keep: sh._element.getparent().remove(sh._element)

def set_runs_text(shape_, texts):
    """Replace text of runs in order, keeping each run's formatting; extra runs are removed."""
    runs = [r for p in shape_.text_frame.paragraphs for r in p.runs]
    for r, t in zip(runs, texts): r.text = t
    for r in runs[len(texts):]: r._r.getparent().remove(r._r)

def by_name(slide, key):
    return [s for s in slide.shapes if f'Shape;{key};' in s.name][0]

def table(slide, x, y, w, cols, rows, widths, size=10, header_size=10, row_h=0.36, mono_cols=(), head_h=0.4):
    gf = slide.shapes.add_table(len(rows) + 1, len(cols), Inches(x), Inches(y), Inches(w), Inches(row_h * (len(rows) + 1)))
    t = gf.table
    tot = sum(widths)
    for i, wd in enumerate(widths): t.columns[i].width = Inches(w * wd / tot)
    def fill_cell(c, text, bold, color, fillc, sz, mono=False):
        c.fill.solid(); c.fill.fore_color.rgb = fillc
        c.margin_left = c.margin_right = Inches(0.08); c.margin_top = c.margin_bottom = Inches(0.04)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        add_runs(p, [(text, {'bold': bold, 'color': color, 'size': sz, 'font': 'Consolas' if mono else FONT})], dict(size=sz, color=color, bold=bold, italic=False, font=FONT))
    for j, h in enumerate(cols): fill_cell(t.cell(0, j), h, True, WHITE, NAVY, header_size)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            fill_cell(t.cell(i, j), v, j == 0, NAVY if j == 0 else INK, LAV if i % 2 == 0 else WHITE, size, mono=(j in mono_cols))
    for i, r in enumerate(t.rows): r.height = Inches(head_h if i == 0 else row_h)
    return gf

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

NOTES = {}

# ================================================================== edit existing slides
s1, s2o, s3o, s4o, s5o, s6o, s7o, s8o, s9o, s10o = slides

# --- title slide
set_runs_text(by_name(s1, 26), ['Review 2 · Implementation & Outputs · Guide: Dr. Katari Balakrishna'])

# --- rationale (old 2)
set_runs_text(by_name(s2o, 50), ['OUTCOME'])
set_runs_text(by_name(s2o, 51), ['Reusable Web Service'])
set_runs_text(by_name(s2o, 52), ['A reusable, multi-organization web service (cloud hosting is planned for the final review), designed for a continuing-ballot majority winner, detectable record changes, and a secret ballot.'])

# --- six techniques (old 3)
set_runs_text(by_name(s3o, 81), ['A relational store keeps structured entities; an append-only JSON event ledger (MongoDB document model) supports audit. Oracle and MongoDB hosting follow.'])
set_runs_text(by_name(s3o, 85), ['Integrity'])
set_runs_text(by_name(s3o, 86), ['UNIQUE and CHECK constraints plus a trigger block duplicate participation independently of application logic; PL/SQL packages follow with Oracle.'])
set_runs_text(by_name(s3o, 91), ['Runs today as one web service (API and UI). Hosting it on a cloud platform is the remaining deployment step.'])

# --- modules (old 6)
mod = [sh for sh in s6o.shapes if sh.has_table][0].table
def set_cell(cell, lead, rest):
    runs = [r for p in cell.text_frame.paragraphs for r in p.runs]
    runs[0].text = lead + rest
    for r in runs[1:]: r._r.getparent().remove(r._r)
set_cell(mod.cell(0, 0), 'Relational core (SQLite now, Oracle planned): ', 'Stores organizations, elections, candidates, voters and admin accounts; constraints, a trigger and views enforce integrity.')
set_cell(mod.cell(1, 0), 'Python · tally engine: ', 'Counts rankings, eliminates the lowest candidate, redistributes ballots, and handles empty elections and exhausted ballots; last-place ties are flagged.')
set_cell(mod.cell(2, 0), 'JSON audit ledger (MongoDB planned): ', 'Stores one hash-chained receipt per ballot, each linked to its predecessor and re-checked by the integrity sweep.')
set_cell(mod.cell(3, 0), 'React + FastAPI · application: ', 'Voter booth, receipt check and admin console over a REST API; coordinates the anonymous dual write. Streamlit is retained.')
set_runs_text(by_name(s6o, 138), ['Core entities:', ' ORGANIZATION · ELECTION · CANDIDATE · VOTER_PARTICIPATION · BALLOT_RANKS · ADMIN_USERS (POSITION is deferred). ', 'Privacy boundary:', ' VOTER_PARTICIPATION and BALLOT_RANKS remain separate; only an anonymous token connects voter participation to ballot content.'])

# --- roadmap (old 9)
set_runs_text(by_name(s9o, 166), ['Three reviews move from design to a finished system'])
set_runs_text(by_name(s9o, 169), ['REVIEW 1 · DONE'])
set_runs_text(by_name(s9o, 170), ['Presented the design, schema, security approach, and planned system architecture.'])
set_runs_text(by_name(s9o, 173), ['REVIEW 2 · NOW'])
set_runs_text(by_name(s9o, 174), ['Working implementation, about 75% of the planned scope, with live outputs and a tamper demonstration.'])
set_runs_text(by_name(s9o, 177), ['FINAL REVIEW'])
set_runs_text(by_name(s9o, 178), ['Oracle + PL/SQL, MongoDB Atlas, cloud deployment, POSITION entity, then comparison with existing e-voting systems.'])
for k in (172, 176): by_name(s9o, k).width = Inches(1.45)
def rebuild_deliverables(shape_):
    p = shape_.text_frame.paragraphs[0]._p
    runs = p.findall(qn('a:r'))
    bold_rpr = copy.deepcopy(runs[0].find(qn('a:rPr'))); norm_rpr = copy.deepcopy(runs[1].find(qn('a:rPr')))
    for el in list(p):
        if el.tag in (qn('a:r'), qn('a:br')): p.remove(el)
    end = p.find(qn('a:endParaRPr'))
    def add(el):
        if end is not None: end.addprevious(el)
        else: p.append(el)
    def run(text, rpr):
        r = etree.SubElement(p, qn('a:r')); r.append(copy.deepcopy(rpr)); t = etree.SubElement(r, qn('a:t')); t.text = text; p.remove(r); add(r)
    def br():
        b = etree.SubElement(p, qn('a:br')); b.append(copy.deepcopy(bold_rpr)); p.remove(b); add(b)
    run('Remaining · Application: ', bold_rpr); run('host the platform live in the cloud', norm_rpr); br()
    run('Database: ', bold_rpr); run('PL/SQL procedures, DCL roles, Oracle and MongoDB scripts', norm_rpr); br()
    run('Verification: ', bold_rpr); run('detect ballots injected without a receipt', norm_rpr)
rebuild_deliverables(by_name(s9o, 180))

# --- thank-you (old 10)
set_runs_text(by_name(s10o, 189), ['PROJECT CONCLUSION · REVIEW 2'])
tb(s10o, 0.38, 1.75, 5.6, 0.3, 'Questions and discussion', size=16, color=INK, bold=True)
tb(s10o, 0.38, 2.25, 5.6, 1.2, [
    [('Source code and documents', {'bold': True, 'color': NAVY})],
    [('github.com/Tharakeshtj/polyvote-election-platform', {'size': 11})],
    [('', {})],
    [('Run it: ', {'bold': True, 'color': NAVY}), ('python -m uvicorn server:app --port 8000', {'font': 'Consolas', 'size': 10})],
], size=12, color=INK, after=3)

# ================================================================== rebuild DFD (old 7) and ER (old 8)
clear(s7o); clear(s8o)
frame(s7o, 'SYSTEM ARCHITECTURE', 'Data flows through three layers, with the ledger kept apart', 8)
MID = RGBColor(0xE9, 0xE9, 0xF3)
# presentation layer
shape(s7o, 0.5, 1.2, 9.0, 0.82, fill=LAV, line=BORDER, lw=1.25, radius=0.08)
tb(s7o, 0.65, 1.26, 5.5, 0.16, 'Presentation layer · React + TypeScript single-page app', size=9, color=NAVY, bold=True)
for x, t, w, ln in [(0.65, 'Voter booth', 1.9, NAVY), (2.7, 'Receipt check', 1.9, NAVY), (4.75, 'Admin console', 1.9, NAVY), (7.35, 'DB Studio (simulated DBA)', 2.0, RED)]:
    label_shape(s7o, x, 1.5, w, 0.38, t, size=10, color=NAVY, fill=WHITE, line=ln, lw=1.25, bold=True, radius=0.12)
# application layer
label_shape(s7o, 0.5, 2.42, 9.0, 0.5, [[('Application layer · FastAPI REST API', {'bold': True}), ('   auth & sessions · election lifecycle & roster · ballot cast (dual write under WRITE_LOCK) · sweep, tally, ledger & receipt endpoints', {})]],
            size=9, color=NAVY, fill=WHITE, line=NAVY, lw=1.5, radius=0.1)
for cx in (1.6, 3.65, 5.7, 8.35): arrow(s7o, cx, 1.9, cx, 2.42, lw=1.25)
tag(s7o, 0.65, 2.1, 1.0, 'JSON / HTTP', size=8)
# stores
shape(s7o, 0.5, 3.35, 6.75, 1.0, fill=RGBColor(0xEC, 0xF4, 0xFB), line=RGBColor(0x8F, 0xB0, 0xD8), lw=1.25, radius=0.06)
tb(s7o, 0.62, 3.4, 6.4, 0.16, 'Relational schema · SQLite · foreign keys ON · trigger · views', size=9, color=NAVY, bold=True)
for i, t in enumerate(['ORGAN-\nIZATION', 'ELECTION', 'CANDIDATE', 'VOTER_\nPARTICIPATION', 'BALLOT_\nRANKS', 'ADMIN_\nUSERS']):
    label_shape(s7o, 0.62 + i * 1.08, 3.66, 1.0, 0.56, t, size=7, color=NAVY, fill=WHITE, line=RGBColor(0x55, 0x55, 0x55), lw=0.9, radius=0.04, bold=(i == 4))
shape(s7o, 7.45, 3.35, 2.05, 1.0, fill=RGBColor(0xFF, 0xF4, 0xE6), line=RGBColor(0xF0, 0xB4, 0x6A), lw=1.25, radius=0.06)
tb(s7o, 7.55, 3.4, 1.9, 0.16, 'Tamper-evident ledger', size=9, color=NAVY, bold=True)
label_shape(s7o, 7.57, 3.66, 1.81, 0.56, 'Hash-chained JSON receipts', size=8.5, color=NAVY, fill=WHITE, line=RGBColor(0x55, 0x55, 0x55), lw=0.9, radius=0.04)
arrow(s7o, 2.6, 2.92, 2.6, 3.35, lw=1.5); tag(s7o, 1.55, 3.03, 2.1, '1–6 · read / write rows')
arrow(s7o, 5.4, 2.92, 5.4, 3.35, color=RED, lw=1.5, dash=True); tag(s7o, 3.85, 3.03, 2.6, '12 · direct UPDATE / DELETE', color=RED, fill=RGBColor(0xFD, 0xEC, 0xEA))
arrow(s7o, 8.5, 2.92, 8.5, 3.35, lw=1.5); tag(s7o, 7.45, 3.03, 2.0, '7 · append SHA-256 receipt')
# engine
shape(s7o, 0.5, 4.75, 9.0, 0.5, fill=RGBColor(0xEE, 0xF8, 0xF0), line=RGBColor(0x7C, 0xCF, 0x91), lw=1.25, radius=0.08)
label_shape(s7o, 0.65, 4.8, 2.7, 0.4, 'Instant-runoff tally (pandas)', size=9.5, color=NAVY, fill=WHITE, line=RGBColor(0x55, 0x55, 0x55), lw=0.9, bold=True, radius=0.1)
label_shape(s7o, 3.65, 4.8, 2.7, 0.4, 'Integrity sweep', size=9.5, color=NAVY, fill=WHITE, line=RGBColor(0x55, 0x55, 0x55), lw=0.9, bold=True, radius=0.1)
label_shape(s7o, 6.65, 4.8, 2.7, 0.4, 'Chain verification', size=9.5, color=NAVY, fill=WHITE, line=RGBColor(0x55, 0x55, 0x55), lw=0.9, bold=True, radius=0.1)
arrow(s7o, 2.0, 4.35, 2.0, 4.8, lw=1.25); tag(s7o, 0.62, 4.45, 1.4, '8 · ranks', size=8)
arrow(s7o, 4.6, 4.35, 4.6, 4.8, lw=1.25); tag(s7o, 3.2, 4.45, 1.55, '9 · recompute hashes', size=8)
arrow(s7o, 7.9, 4.35, 5.9, 4.8, lw=1.25); tag(s7o, 6.4, 4.45, 1.55, '10 · cross-check', size=8)
arrow(s7o, 8.9, 4.35, 8.9, 4.8, lw=1.25); tag(s7o, 8.1, 4.5, 1.1, 'verify links', size=8)

frame(s8o, 'ER DIAGRAM & RELATIONAL SCHEMA', 'Tables and ledger are linked by token, not by identity', 9)
s8o.shapes.add_picture(ER_PNG, Inches(0.85), Inches(1.15), width=Inches(8.3))

# ================================================================== new slides
# ---- NEW A: Review 1 -> Review 2 summary
sA = new_slide(); frame(sA, 'REVIEW 2 · WHERE WE STAND', 'What we submitted, what we built, what changed', 2)
cards = [
    ('SUBMITTED', 'Review 1', 'Design, relational schema and ER diagram, security approach, literature review, and a planned architecture on Oracle, MongoDB and Streamlit.'),
    ('BUILT', 'Since Review 1', 'A working system: React voter booth and admin console, FastAPI service, SQLite schema with trigger and views, instant-runoff tally, hash-chained receipts and a live tamper test.'),
    ('CHANGED', 'And why', 'SQLite stands in for Oracle and a JSON document ledger for MongoDB; React + FastAPI now sits beside Streamlit; an ADMIN_USERS table was added.'),
]
for i, (tg, head, body) in enumerate(cards):
    x = 0.5 + i * 3.09
    card(sA, x, 1.2, 2.83, 2.5)
    chip(sA, x + 0.2, 1.34, tg)
    tb(sA, x + 0.2, 1.72, 2.45, 0.28, head, size=15, color=NAVY, bold=True)
    tb(sA, x + 0.2, 2.08, 2.45, 1.5, body, size=12, color=INK)
card(sA, 0.5, 3.88, 9.0, 1.2, fill=LAV)
tb(sA, 0.75, 3.96, 1.7, 0.7, '75%', size=44, color=NAVY, bold=True, anchor=MSO_ANCHOR.MIDDLE)
tb(sA, 0.75, 4.64, 1.9, 0.3, 'of the Review 1 scope', size=11, color=MUTED)
tb(sA, 2.8, 4.02, 6.5, 1.0, [
    [('Left for the final review: ', {'bold': True, 'color': NAVY}), ('Oracle with PL/SQL procedures and DCL, MongoDB Atlas, cloud deployment, and the POSITION entity.', {})],
    [('', {})],
    [('Next: ', {'bold': True, 'color': NAVY}), ('the design recap, updated diagrams, then the running system and its outputs.', {})],
], size=12, color=INK, after=2)

# ---- NEW B: database integrity
sB = new_slide(); frame(sB, 'DATABASE INTEGRITY', 'The database itself refuses invalid votes', 10)
table(sB, 0.5, 1.2, 9.0, ['Rule', 'Enforced by', 'Response when we tried to break it'], [
    ['One vote per voter', 'TRIGGER trg_block_duplicate_vote', 'DBMS Trigger Violation: Voter has already submitted a ballot.'],
    ['Top three ranks only', 'CHECK (preference_rank BETWEEN 1 AND 3)', 'CHECK constraint failed: preference_rank BETWEEN 1 AND 3'],
    ['No candidate twice on one ballot', 'PRIMARY KEY (ballot_token, candidate_id)', 'UNIQUE constraint failed: BALLOT_RANKS.ballot_token, BALLOT_RANKS.candidate_id'],
    ['Only real candidates', 'FOREIGN KEY → CANDIDATE', 'FOREIGN KEY constraint failed'],
], [2.2, 3.0, 3.8], size=10, row_h=0.6, mono_cols=(1,))
card(sB, 0.5, 4.2, 4.4, 0.95, fill=LAV, lw=1.25)
tb(sB, 0.68, 4.3, 4.1, 0.8, [[('Live views', {'bold': True, 'color': NAVY})], [('VIEW_ELECTION_TURNOUT and VIEW_FIRST_PREFERENCES feed the dashboards: 45 of 60 voters, 75% turnout.', {})]], size=11, color=INK, after=3)
card(sB, 5.1, 4.2, 4.4, 0.95, fill=LAV, lw=1.25)
tb(sB, 5.28, 4.3, 4.1, 0.8, [[('Each statement ran on the live database', {'bold': True, 'color': NAVY})], [('and was rolled back; the messages shown are the database’s own, not the application’s.', {})]], size=11, color=INK, after=3)

# ---- NEW C: voter journey
sC = new_slide(); frame(sC, 'VOTER SIDE', 'Voting takes three steps and ends with a receipt', 11)
H = 2.25
items = [('01_voter_home.png', '1 · Choose an open election', 'Only elections in the Voting phase can be entered.'),
         ('03_ballot_partial.png', '2 · Rank three candidates', 'Tap in order of preference; review before casting.'),
         ('05_receipt.png', '3 · Keep the receipt token', 'It proves the ballot is sealed, not how you voted.')]
x = 0.5
widths = []
for f, _, _ in items:
    from PIL import Image
    w_, h_ = Image.open(os.path.join(SCR, f)).size; widths.append(H * w_ / h_)
gap = (9.0 - sum(widths)) / 2
for (f, head, sub), wd in zip(items, widths):
    pic(sC, f, x, 1.25, h=H)
    tb(sC, x, 1.25 + H + 0.12, max(wd, 2.4), 0.25, head, size=12.5, color=NAVY, bold=True)
    tb(sC, x, 1.25 + H + 0.42, max(wd, 2.4) - 0.1, 0.55, sub, size=11, color=INK)
    x += wd + gap
card(sC, 0.5, 4.5, 9.0, 0.7, fill=LAV, lw=1.25)
tb(sC, 0.7, 4.58, 8.6, 0.55, [[('Guards in the flow: ', {'bold': True, 'color': NAVY}), ('wrong password is rejected, a voter who already voted is refused, and the ballot cannot be changed once cast.', {})]], size=11.5, color=INK, anchor=MSO_ANCHOR.MIDDLE)

# ---- NEW D: dual write and privacy
sD = new_slide(); frame(sD, 'PRIVACY BY DESIGN', 'One vote becomes two records that cannot be joined', 12)
label_shape(sD, 0.5, 1.5, 1.7, 0.9, [[('Voter signs in', {'bold': True})], [('registration no. + password', {'size': 9})]], size=11, color=NAVY, fill=LAV, line=NAVY, lw=1.5, radius=0.12)
arrow(sD, 2.2, 1.95, 2.75, 1.95)
shape(sD, 2.75, 1.2, 3.85, 3.0, fill=None, line=MUTED, lw=1.0, dash=True, radius=0.04)
tb(sD, 2.9, 1.27, 3.5, 0.2, 'One database transaction', size=10, color=MUTED, bold=True)
label_shape(sD, 2.95, 1.6, 3.45, 0.8, [[('VOTER_PARTICIPATION', {'bold': True})], [('has_voted = 1   (identity side)', {'size': 9.5})]], size=11, color=NAVY, fill=WHITE, line=NAVY, lw=1.5, radius=0.1)
tb(sD, 2.95, 2.5, 3.45, 0.3, 'privacy boundary: no voter ID is ever stored with a ballot', size=9.5, color=RED, italic=True, align=PP_ALIGN.CENTER)
label_shape(sD, 2.95, 2.95, 3.45, 0.95, [[('BALLOT_RANKS', {'bold': True})], [('random ballot_token + 3 ranked candidates', {'size': 9.5})], [('(ballot side)', {'size': 9.5})]], size=11, color=NAVY, fill=WHITE, line=NAVY, lw=1.5, radius=0.1)
arrow(sD, 6.6, 3.4, 7.15, 3.4)
label_shape(sD, 7.15, 2.85, 2.35, 1.1, [[('Ledger append', {'bold': True})], [('SHA-256 of the ranks + prev_hash, sealed as curr_hash', {'size': 9.5})]], size=11, color=NAVY, fill=RGBColor(0xFF, 0xF4, 0xE6), line=RGBColor(0xF0, 0xB4, 0x6A), lw=1.5, radius=0.1)
arrow(sD, 8.3, 2.85, 8.3, 2.4)
label_shape(sD, 7.15, 1.5, 2.35, 0.9, [[('Receipt token', {'bold': True})], [('returned to the voter', {'size': 9.5})]], size=11, color=NAVY, fill=LAV, line=NAVY, lw=1.5, radius=0.12)
for i, (h, b) in enumerate([('Atomic', 'The voter flag and the ballot rows commit together, then the receipt is appended.'),
                            ('Serialized', 'A server-side write lock keeps simultaneous ballots from corrupting the ledger.'),
                            ('Verifiable', 'Voters can look their token up later without revealing their choices.')]):
    x = 0.5 + i * 3.09
    card(sD, x, 4.38, 2.83, 0.85, fill=LAV, lw=1.25)
    tb(sD, x + 0.15, 4.45, 2.55, 0.75, [[(h, {'bold': True, 'color': NAVY})], [(b, {'size': 9.5})]], size=11, color=INK, after=1)

# ---- NEW E: instant-runoff
sE = new_slide(); frame(sE, 'TALLYING ENGINE', 'Instant-runoff counts until someone holds a majority', 13)
cd = CategoryChartData(); cd.categories = ['Round 1', 'Round 2', 'Round 3', 'Round 4']
SER = [('Chaitanya Reddy', [9, 11, 15, 23], GREEN, WHITE), ('Diya Sharma', [10, 13, 16, 22], NAVY, WHITE),
       ('Arun Kumar', [10, 12, 14, None], RGBColor(0x8D, 0xA0, 0xD0), NAVY), ('Eshaan Iyer', [8, 9, None, None], RGBColor(0xC8, 0xCE, 0xE3), NAVY),
       ('Bhavya Singh', [8, None, None, None], RGBColor(0xE4, 0xE6, 0xF0), NAVY)]
for n, v, _, _ in SER: cd.add_series(n, v)
gf = sE.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, Inches(0.4), Inches(1.15), Inches(5.6), Inches(4.0), cd)
ch = gf.chart; ch.has_legend = True; ch.legend.position = XL_LEGEND_POSITION.BOTTOM; ch.legend.include_in_layout = False
ch.legend.font.size = Pt(10); ch.legend.font.name = FONT; ch.legend.font.color.rgb = INK
ch.plots[0].gap_width = 45; ch.plots[0].overlap = 100
for ser, (_, _, col, lab) in zip(ch.plots[0].series, SER):
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = col
    dl = ser.data_labels; dl.show_value = True; dl.number_format = '0'; dl.number_format_is_linked = False
    dl.font.size = Pt(10); dl.font.name = FONT; dl.font.color.rgb = lab; dl.position = XL_LABEL_POSITION.CENTER
va = ch.value_axis; va.maximum_scale = 45; va.minimum_scale = 0; va.major_unit = 15; va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = BORDER; va.format.line.fill.background()
va.tick_labels.font.size = Pt(10); va.tick_labels.font.name = FONT; va.tick_labels.font.color.rgb = MUTED
ca = ch.category_axis; ca.tick_labels.font.size = Pt(10.5); ca.tick_labels.font.name = FONT; ca.tick_labels.font.color.rgb = INK
ca.format.line.color.rgb = BORDER
ch.has_title = False
card(sE, 6.2, 1.2, 3.3, 1.45, fill=LAV, lw=1.25)
tb(sE, 6.38, 1.3, 3.0, 1.3, [[('Chaitanya Reddy wins', {'bold': True, 'color': GREEN, 'size': 14})], [('23 of 45 continuing ballots (51.1%) in round 4, against 22 for Diya Sharma.', {})]], size=11.5, color=INK, after=3)
tb(sE, 6.2, 2.85, 3.3, 2.3, [
    [('How it runs', {'bold': True, 'color': NAVY})],
    [('Count each ballot’s top continuing choice.', {})],
    [('No majority? Eliminate the last-place candidate and move those ballots to their next choice.', {})],
    [('Edge cases: exhausted ballots, empty elections, and last-place ties are flagged in the interface.', {})],
], size=11, color=INK, after=5)

# ---- NEW F: hash-chained ledger
sF = new_slide(); frame(sF, 'AUDIT LEDGER', 'Every ballot is sealed in a hash chain', 14)
blocks = [(1, '0f2da608…', '98f83226…', '00000000…', '5906eaba…'), (2, '050556d2…', '470ef925…', '5906eaba…', '077a697b…'), (3, 'de410a8a…', '98f83226…', '077a697b…', 'e50bbfe1…')]
for i, (idx, tok, vh, ph, ch_) in enumerate(blocks):
    x = 0.5 + i * 3.09
    card(sF, x, 1.2, 2.83, 2.1)
    chip(sF, x + 0.15, 1.3, f'Block {idx}')
    rows_ = [('ballot_token', tok), ('vote_data_hash', vh), ('prev_hash', ph), ('curr_hash', ch_)]
    for k, (lab, val) in enumerate(rows_):
        yy = 1.68 + k * 0.38
        tb(sF, x + 0.18, yy, 1.2, 0.3, lab, size=10, color=MUTED, anchor=MSO_ANCHOR.MIDDLE)
        tb(sF, x + 1.38, yy, 1.35, 0.3, val, size=10.5, color=(GREEN if lab == 'prev_hash' and idx > 1 else NAVY), bold=(lab in ('prev_hash', 'curr_hash')), anchor=MSO_ANCHOR.MIDDLE).text_frame.paragraphs[0].runs[0].font.name = 'Consolas'
    if i < 2:
        arrow(sF, x + 2.83, 2.6, x + 3.09, 2.6, color=GREEN, lw=2)
tb(sF, 0.5, 3.4, 9.0, 0.22, 'Block 2’s prev_hash equals block 1’s curr_hash, and so on: editing any block breaks every link after it.', size=10.5, color=MUTED, italic=True)
for i, (h, b) in enumerate([('Seal', 'vote_data_hash = SHA-256 of the ballot’s ranks; curr_hash covers the whole block.'),
                            ('Chain check', 'audit_ledger.py recomputes every hash and link: 45 of 45 blocks intact.'),
                            ('Ballot check', 'The integrity sweep recomputes each ballot from the database and compares it with its receipt.')]):
    x = 0.5 + i * 3.09
    card(sF, x, 3.8, 2.83, 1.35, fill=LAV, lw=1.25)
    tb(sF, x + 0.18, 3.9, 2.5, 1.2, [[(h, {'bold': True, 'color': NAVY, 'size': 12.5})], [(b, {})]], size=11, color=INK, after=3)

# ---- NEW G: admin console
sG = new_slide(); frame(sG, 'ADMINISTRATOR SIDE', 'Officers run each election through a guarded lifecycle', 15)
pic(sG, '11_admin_overview.png', 0.5, 1.2, w=5.0)
pic(sG, '10_admin_elections.png', 0.5, 1.2 + 5.0 * 1098 / 2136 + 0.15, w=5.0)
card(sG, 5.75, 1.2, 3.75, 3.95, fill=LAV, lw=1.25)
tb(sG, 5.95, 1.3, 3.4, 0.25, 'Election lifecycle', size=14, color=NAVY, bold=True)
for i, (h, b) in enumerate([('Nominations', 'Add candidates; build the roster by hand or in bulk.'),
                            ('Voting', 'Candidates are locked; voters cast ballots; simulation tools for testing.'),
                            ('Closed', 'No more votes; run the integrity sweep, then count.')]):
    yy = 1.75 + i * 0.95
    label_shape(sG, 5.95, yy, 0.34, 0.34, str(i + 1), size=11, color=WHITE, fill=NAVY, bold=True, radius=0.5)
    tb(sG, 6.4, yy - 0.02, 2.95, 0.9, [[(h, {'bold': True, 'color': NAVY, 'size': 12})], [(b, {})]], size=10.5, color=INK, after=1)
tb(sG, 5.95, 4.6, 3.4, 0.5, 'Each change asks for confirmation, and a closed election cannot be reopened.', size=10.5, color=MUTED, italic=True)

# ---- NEW H: tamper demo
sH = new_slide(); frame(sH, 'LIVE TAMPER TEST', 'A rogue DBA edits the database and the sweep catches it', 16)
steps = [('Edit', 'In DB Studio we re-assigned one ballot’s first choice.'),
         ('Delete', 'We deleted two ballot rows, including a voter’s own.'),
         ('Sweep', 'Run integrity sweep: every sealed ballot is recomputed and compared.')]
for i, (h, b) in enumerate(steps):
    yy = 1.25 + i * 1.12
    label_shape(sH, 0.5, yy, 0.38, 0.38, str(i + 1), size=12, color=WHITE, fill=NAVY, bold=True, radius=0.5)
    tb(sH, 1.05, yy - 0.02, 2.55, 1.0, [[(h, {'bold': True, 'color': NAVY, 'size': 13})], [(b, {})]], size=10.5, color=INK, after=2)
card(sH, 0.5, 4.65, 3.1, 0.6, fill=RGBColor(0xFD, 0xEC, 0xEA), lw=1.25)
tb(sH, 0.65, 4.7, 2.85, 0.5, [[('Result: 3 of 3 flagged', {'bold': True, 'color': RED}), (' (1 modified, 2 deleted)', {})]], size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE)
pic(sH, '17_sweep_tampered.png', 3.85, 1.25, w=5.65)

# ---- NEW I: verification results
sI = new_slide(); frame(sI, 'VERIFICATION', 'Seven checks, seven expected outcomes', 17)
table(sI, 0.5, 1.2, 9.0, ['Check', 'Expected', 'Observed'], [
    ['Same voter votes twice', 'Refused', 'You have already voted in this election.'],
    ['Wrong password at sign-in', 'Rejected', 'Incorrect password.'],
    ['Ledger hash chain', 'Intact', 'Chain intact across all 45 receipts'],
    ['1 ballot re-ranked, 2 deleted in the database', 'All three flagged', '1 modified and 2 deleted detected'],
    ['Voter checks a deleted ballot’s receipt', 'Warned', 'Recorded, but missing from the count'],
    ['Counts after tampering', 'Mismatch visible', '43 ballots vs 45 receipts vs 45 voted'],
    ['Ranked-choice majority', 'Winner holds a majority', 'Chaitanya Reddy: 23 of 45 (51.1%)'],
], [3.4, 2.0, 3.6], size=10.5, row_h=0.46)
tb(sI, 0.5, 4.95, 9.0, 0.3, 'Outputs captured on a demo election: 60 registered voters, 45 ballots cast, five candidates.', size=10.5, color=MUTED, italic=True)

# ---- NEW J: implementation status chart
sJ = new_slide(); frame(sJ, 'IMPLEMENTATION STATUS', 'About 75% of the Review 1 scope is implemented', 18)
cd = CategoryChartData(); cd.categories = ['Core features (7)', 'Modules (4)', 'Deliverables (3)', 'Overall (14)']
cd.add_series('Implemented', [64, 91, 80, 75])
gf = sJ.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.4), Inches(1.15), Inches(5.2), Inches(3.95), cd)
ch = gf.chart; ch.has_legend = False; ch.has_title = False
pl = ch.plots[0]; pl.gap_width = 55; pl.vary_by_categories = False
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = NAVY
pt = ser.points[3]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = GREEN
dl = ser.data_labels; dl.show_value = True; dl.number_format = '0"%"'; dl.number_format_is_linked = False
dl.font.size = Pt(12); dl.font.bold = True; dl.font.name = FONT; dl.font.color.rgb = NAVY; dl.position = XL_LABEL_POSITION.OUTSIDE_END
va = ch.value_axis; va.maximum_scale = 100; va.minimum_scale = 0; va.major_unit = 25; va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = BORDER; va.format.line.fill.background()
va.tick_labels.font.size = Pt(10); va.tick_labels.font.name = FONT; va.tick_labels.font.color.rgb = MUTED; va.tick_labels.number_format = '0"%"'; va.tick_labels.number_format_is_linked = False
ca = ch.category_axis; ca.tick_labels.font.size = Pt(10.5); ca.tick_labels.font.name = FONT; ca.tick_labels.font.color.rgb = INK; ca.format.line.color.rgb = BORDER
card(sJ, 5.85, 1.2, 3.65, 1.75)
tb(sJ, 6.05, 1.3, 3.3, 1.6, [[('Done', {'bold': True, 'color': GREEN, 'size': 13})],
                              [('Multi-tenant schema, trigger and views, instant-runoff tally, hash-chained ledger, tamper detection, voter and admin applications.', {})]], size=11, color=INK, after=3)
card(sJ, 5.85, 3.15, 3.65, 1.95)
tb(sJ, 6.05, 3.25, 3.3, 1.8, [[('Remaining for the final review', {'bold': True, 'color': AMBER, 'size': 13})],
                               [('Oracle with PL/SQL procedures and DCL', {})], [('MongoDB Atlas for the ledger', {})], [('Cloud deployment', {})], [('POSITION entity', {})]], size=11, color=INK, after=3)

# ---- NEW K: changes vs plan
sK = new_slide(); frame(sK, 'PLAN VS BUILD', 'Where the build differs from the Review 1 plan, and why', 19)
table(sK, 0.5, 1.2, 9.0, ['Area', 'Review 1 plan', 'Built for Review 2', 'Why'], [
    ['Relational DBMS', 'Oracle Autonomous DB with PL/SQL', 'SQLite with trigger, views, constraints', 'Zero-setup development; schema kept portable'],
    ['NoSQL ledger', 'MongoDB Atlas', 'Hash-chained JSON documents', 'Same document model without a hosted cluster'],
    ['Frontend', 'Streamlit', 'React + FastAPI; Streamlit kept', 'Separate voter and admin experiences, mobile support'],
    ['Schema', 'Five core tables', '+ ADMIN_USERS; POSITION deferred', 'Officer logins needed a table'],
    ['Lifecycle', 'Timestamp-driven procedures', 'Guarded Nominations → Voting → Closed', 'SQLite has no stored procedures'],
], [1.5, 2.2, 2.8, 2.7], size=10, row_h=0.56)
card(sK, 0.5, 4.5, 9.0, 0.65, fill=LAV, lw=1.25)
tb(sK, 0.7, 4.55, 8.6, 0.55, [[('Unchanged targets: ', {'bold': True, 'color': NAVY}), ('Oracle with PL/SQL, MongoDB Atlas and cloud deployment remain the goals for the final review; the code is structured so they are a migration, not a rewrite.', {})]], size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE)

# ================================================================== footers and order
order = [s1, sA, s2o, s3o, s4o, s5o, s6o, s7o, s8o, sB, sC, sD, sE, sF, sG, sH, sI, sJ, sK, s9o, s10o]
lst = prs.slides._sldIdLst
ids = {s.slide_id: el for s, el in zip(prs.slides, list(lst))}
els = [ids[s.slide_id] for s in order]
for el in list(lst): lst.remove(el)
for el in els: lst.append(el)
for n, s in enumerate(order, start=1):
    for sh in s.shapes:
        if sh.has_text_frame and re.match(r'BACSE202 – Database Systems \| Review', sh.text_frame.text):
            runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
            runs[0].text = FOOT.format(n=n)
            for r in runs[1:]: r._r.getparent().remove(r._r)

# ================================================================== speaker notes
S = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.json'), encoding='utf-8'))
for n, s in enumerate(order, start=1):
    if str(n) in S: notes(s, S[str(n)])
prs.save(OUT)
print('saved', OUT, len(order), 'slides')

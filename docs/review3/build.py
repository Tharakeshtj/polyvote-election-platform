"""Build docs/PolyVote_Review_III.docx from the Review II template, the experiment results and the figures.

    python docs/review3/build.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import data                      # noqa: E402
import sec1_3, sec4_5, sec6_7, sec8_10  # noqa: E402
from helpers import Ctx          # noqa: E402

ROOT = data.ROOT
TEMPLATE = ROOT / 'docs' / 'PolyVote_Review_II.docx'
OUT = ROOT / 'docs' / 'PolyVote_Review_III.docx'

S = data.load()
S['_refs'] = str(HERE / 'references_ieee.txt')

labels = {}
for _ in range(2):               # second pass resolves "Figure N"/"Table N" cross-references
    c = Ctx(TEMPLATE, labels)
    for mod in (sec1_3, sec4_5, sec6_7, sec8_10):
        mod.build(c, S)
    c.page_numbers()
    labels = c.labels
c.save(OUT)
print('wrote', OUT, '| figures', c.fig, 'tables', c.tab)

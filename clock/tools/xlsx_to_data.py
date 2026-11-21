"""Build clock/data.js from the History Clock Excel (sheet 'WF Tekstid ENG').

Usage:  python3 -I tools/xlsx_to_data.py History_Clock.xlsx > data.js

Future years (2027+) get a status label:
  scheduled  certain: astronomy, calendar and computer-clock rollovers, signals arriving, set dates
  perhaps    guesses, plans and projections, and anything marked (?)
  scifi      events from fiction
  fact       anniversaries and other computed facts (no label)
Adjust the OVERRIDE table below to move a year between kinds.
"""
import json, re, sys
import openpyxl

SCIFI = re.compile(r"Star Trek|Terminator|RoboCop|Futurama|Hunger Games|Zero Wing|Sci-?Fi|SciFi|^SF:|Babylon 5|Bicentennial Man|Outward Urge|Invitation to the Game|The Fun They Had|Shiva|Galactic North|\"2312\"", re.I)
FACT = re.compile(r"\b(yrs|years) (from|fom)\b|\|\s*\d{3,4}\s*\|\s*\(|\b\d{3,4}\s*\(\d{4}[,)]|\b\d{3,4}\s*\(\d{3} BC\)|\b\d{3,4}\s*\|\s*\(|Declaration of Independence \d{3}|Cambridge \| 1000|Knights Templar 1000|Mickey Mouse 400|State of Israel 300|Yellowstone National Park 450|Schrödinger's cat - 300|Mein Kampf and The Great Gatsby - 500")
PERHAPS_YEARS = {2030, 2041, 2042, 2043, 2045, 2049, 2056, 2122, 2129, 2200, 2350}
OVERRIDE = {2304: "fact", 2310: "perhaps"}  # year: kind

def clean(t):
    t = str(t).replace("-\n", "-").replace("\n", " ")
    return re.sub(r"\s{2,}", " ", t).strip()

def status(y, raw):
    if y in OVERRIDE: return OVERRIDE[y]
    if "(?)" in raw or y in PERHAPS_YEARS: return "perhaps"
    if SCIFI.search(raw): return "scifi"
    if FACT.search(raw): return "fact"
    return "scheduled"

wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
ws = wb["WF Tekstid ENG"]
ev = {}
for row in ws.iter_rows(min_row=3, values_only=True):
    if row[0] is None or row[1] is None: continue
    y = int(str(row[0]))
    raw = str(row[1]).replace("\n", " | ")
    e = {"t": clean(row[1])}
    if y > 2026: e["s"] = status(y, raw)
    ev[y] = e

out = ["// History Clock event data, English. Generated from the Excel by tools/xlsx_to_data.py: edit the Excel, not this file.",
       "// t = dial text; s = future status: scheduled | perhaps | scifi | fact (no label)",
       "window.HC_EVENTS = {"]
keys = sorted(ev)
for i, y in enumerate(keys):
    out.append(f"  {y}: {json.dumps(ev[y], ensure_ascii=False)}{',' if i < len(keys)-1 else ''}")
out.append("};")
print("\n".join(out))

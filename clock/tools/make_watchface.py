#!/usr/bin/env python3
"""Generate the History Clock watch face (Watch Face Format) from the simulator's design values.

Writes clock/watchface/watchface/src/main/res/raw/watchface.xml.
Edit this script, never the generated XML.

v0.1 is the first test on a real watch. It checks the whole chain (cloud build, install over Wi-Fi)
and the risky parts of the design:
  - the year as the time (HHMM read as a number, leading zeros dropped, AD hanging to its left)
  - colour drift: background and ink blend between keyframe years, minute by minute
  - the era ring with the current era wider and stronger, and the ruby marker moving round it
  - one frieze (the drafting ruler) and the seconds glow travelling round it
  - two event lines of different widths (the frieze-shaped text area), with fixed sample text
  - the day-and-date pill
  - always-on mode
Fixed sample text only: the companion app that supplies the real events comes later.
"""
import math
import os
import xml.sax.saxutils as sx

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'watchface', 'watchface', 'src', 'main', 'res', 'raw', 'watchface.xml')

C = 225                         # centre of the 450 x 450 face
R = 211                         # era ring radius
NOWA = (20 + 26 / 60) * 15      # "now" (2026) on the ring, degrees
FRIEZE_R, FRIEZE_W = 186, 14    # frieze outer radius and width
CLEAR = 6                       # clearance inside the frieze

# minute of the day = the year's index on the clock (0..1439)
I = '([HOUR_0_23]*60+[MINUTE])'
YEAR = '([HOUR_0_23]*100+[MINUTE])'


def idx(year):
    return (year // 100) * 60 + year % 100


# Colour keyframes, as in the simulator (clock/index.html, KF): year, base, glow 1, glow 2, ink, frieze
KF = [
    (0,    '#16070a', '#8f1d17', '#8a5a2b', '#f2e4cf', '#c9a06a'),
    (300,  '#13060f', '#6e1a44', '#a07a2a', '#f1e2d0', '#c9a24a'),
    (550,  '#0d0816', '#4b2a6c', '#b08a30', '#efe3cf', '#d0aa50'),
    (800,  '#0a0f0d', '#2f4b3a', '#8a6a30', '#e8e2cc', '#b89a5a'),
    (1200, '#080a18', '#24307a', '#a8842e', '#ecdcae', '#c9a24a'),
    (1450, '#0c0812', '#6a1e2a', '#2a3a7a', '#eedcc0', '#c9a24a'),
    (1550, '#0e0905', '#6a4a20', '#b07a30', '#f0dfbc', '#e0c48a'),
    (1700, '#0b0a10', '#3a2a4c', '#9a6a30', '#eedcc0', '#d8bf8a'),
    (1850, '#0a0b0d', '#3a4250', '#8a4a2a', '#e8e4dc', '#b8a890'),
    (1950, '#06090d', '#1d3a5a', '#1f6a7a', '#e6edf3', '#9fc3ff'),
    (2026, '#05070f', '#263a6a', '#1f6a7a', '#e4ebf7', '#a8c0ff'),
    (2100, '#030410', '#5b3fa8', '#1f7a8c', '#dfe6ff', '#c4b8ff'),
    (2359, '#04020c', '#7a3a9a', '#2a5a9a', '#e6e0ff', '#cdb4ff'),
]
COL = {'base': 1, 'g1': 2, 'g2': 3, 'ink': 4, 'pat': 5}

BANDS = [('ANTIQUITY', 0, 75), ('MEDIEVAL', 75, 225), ('EARLY MODERN', 225, 270),
         ('MODERN', 270, NOWA), ('FUTURE', NOWA, 360)]


def rgb(h):
    h = h.lstrip('#')
    return [int(h[k:k + 2], 16) for k in (0, 2, 4)]


def channel(key, ch):
    """Piecewise-linear expression for one colour channel across the keyframes, as a function of I."""
    pts = [(idx(k[0]), rgb(k[COL[key]])[ch]) for k in KF]
    expr = str(pts[-1][1])
    for n in range(len(pts) - 2, -1, -1):
        (x0, v0), (x1, v1) = pts[n], pts[n + 1]
        seg = f'({v0}+({v1 - v0})*({I}-{x0})/{x1 - x0})' if v1 != v0 else str(v0)
        expr = f'(({x1}>{I})?{seg}:{expr})'
    return f'round({expr})'   # colour channels must be whole numbers 0..255


def drift(key, alpha=255):
    """A colour that follows the drift (Transform target="color" value=...)."""
    r, g, b = (channel(key, c) for c in range(3))
    if alpha == 255:
        return f'colorRgb({r},{g},{b})'
    return f'colorArgb({alpha},{r},{g},{b})'


def pt(a, r):
    a = math.radians(a)
    return C + r * math.sin(a), C - r * math.cos(a)


def f1(x):
    return f'{x:.1f}'


def esc(s):
    return sx.quoteattr(s)


# ---------------------------------------------------------------------------------------------
def background():
    # base colour, plus a soft glow from the upper right (light always comes from there)
    s = ['<Group name="background" x="0" y="0" width="450" height="450">',
         '<Variant mode="AMBIENT" target="alpha" value="0"/>',
         '<PartDraw x="0" y="0" width="450" height="450">',
         f'<Rectangle x="0" y="0" width="450" height="450"><Fill color="#000000"><Transform target="color" value="{drift("base")}"/></Fill></Rectangle>',
         '</PartDraw>']
    # glow 1: concentric discs, each faint, centred upper right: an approximated radial gradient
    gx, gy = 330, 110
    for rad, a in [(300 - 22 * k, 10) for k in range(11)]:   # many faint discs: no visible rings
        s.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="{a}">'
                 f'<Ellipse x="{gx - rad}" y="{gy - rad}" width="{2 * rad}" height="{2 * rad}">'
                 f'<Fill color="#ffffff"><Transform target="color" value="{drift("g1")}"/></Fill></Ellipse></PartDraw>')
    # glow 2, lower left, weaker
    gx, gy = 110, 360
    for rad, a in [(220 - 20 * k, 7) for k in range(8)]:
        s.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="{a}">'
                 f'<Ellipse x="{gx - rad}" y="{gy - rad}" width="{2 * rad}" height="{2 * rad}">'
                 f'<Fill color="#ffffff"><Transform target="color" value="{drift("g2")}"/></Fill></Ellipse></PartDraw>')
    s.append('</Group>')
    return '\n'.join(s)


def frieze():
    """The 1900s drafting ruler: ticks every 1.5 degrees, longer every 7.5 and 15."""
    fo, fi = FRIEZE_R, FRIEZE_R - FRIEZE_W
    lines = []
    for n in range(240):
        a = n * 1.5
        big, half = n % 10 == 0, n % 5 == 0
        r2 = fi if big else (fi + FRIEZE_W * .35 if half else fi + FRIEZE_W * .55)
        x1, y1 = pt(a, fo - 1)
        x2, y2 = pt(a, r2)
        lines.append(f'<Line startX="{f1(x1)}" startY="{f1(y1)}" endX="{f1(x2)}" endY="{f1(y2)}">'
                     f'<Stroke color="#ffe6d2a0" thickness="{1.4 if big else 1.1}"/></Line>')   # v0.1: fixed warm gold; drift comes later
    return ('<Group name="frieze" x="0" y="0" width="450" height="450">'
            '<Variant mode="AMBIENT" target="alpha" value="0"/>'
            '<PartDraw x="0" y="0" width="450" height="450" alpha="90">' + ''.join(lines) + '</PartDraw></Group>')


def seconds_glow():
    """A light travelling once round the frieze every minute: bright segments whose alpha
    depends on how far behind the moving head they are (a 100 degree tail)."""
    fo, fi = FRIEZE_R, FRIEZE_R - FRIEZE_W
    head = '([SECOND]*6+[MILLISECOND]*0.006)'
    tail = 100
    parts = []
    for n in range(72):                  # one segment per 5 degrees
        a = n * 5
        lag = f'(({head}-{a}+360)%360)'   # degrees behind the head, 0..360
        alpha = f'(({tail}>{lag})?(230*(1-{lag}/{tail})*(1-{lag}/{tail})):0)'
        ticks = []
        for k in range(3):               # three ruler ticks per segment, matching the frieze
            b = a + k * 1.5
            x1, y1 = pt(b, fo - 1)
            x2, y2 = pt(b, fi + FRIEZE_W * .3)
            ticks.append(f'<Line startX="{f1(x1)}" startY="{f1(y1)}" endX="{f1(x2)}" endY="{f1(y2)}">'
                         f'<Stroke color="#ffffff" thickness="1.6"/></Line>')
        parts.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="0">'
                     f'<Transform target="alpha" value="{alpha}"/>' + ''.join(ticks) + '</PartDraw>')
    return ('<Group name="seconds_glow" x="0" y="0" width="450" height="450">'
            '<Variant mode="AMBIENT" target="alpha" value="0"/>' + ''.join(parts) + '</Group>')


def era_ring():
    s = ['<Group name="era_ring" x="0" y="0" width="450" height="450">']
    for name, a1, a2 in BANDS:
        g = 1.4
        dash = ' dashIntervals="2 5"' if name == 'FUTURE' else ''
        i1, i2 = round(a1 * 4), round(a2 * 4)
        on = f'(({I}>={i1})&amp;&amp;({i2}>{I}))'   # XML-escaped &&
        # faint line for every era
        s.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="56">'
                 f'<Arc centerX="{C}" centerY="{C}" width="{2 * R}" height="{2 * R}" startAngle="{a1 + g:.2f}" endAngle="{a2 - g:.2f}">'
                 f'<Stroke color="#ffffff" thickness="3" cap="ROUND"{dash}/></Arc></PartDraw>')
        # the current era: same see-through white, wider and stronger
        s.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="0">'
                 f'<Transform target="alpha" value="({on}?122:0)"/>'
                 f'<Variant mode="AMBIENT" target="alpha" value="0"/>'
                 f'<Arc centerX="{C}" centerY="{C}" width="{2 * R}" height="{2 * R}" startAngle="{a1 + g:.2f}" endAngle="{a2 - g:.2f}">'
                 f'<Stroke color="#ffffff" thickness="4.5" cap="ROUND"{dash}/></Arc></PartDraw>')
        # era name along the ring: upright on the lower half
        mid = (a1 + a2) / 2
        low = 90 < mid < 270
        rr = 201 if low else 192
        if low:
            sa, ea, d = a2 - 1, a1 + 1, 'COUNTER_CLOCKWISE'
        else:
            sa, ea, d = a1 + 1, a2 - 1, 'CLOCKWISE'
        s.append(f'<PartText x="0" y="0" width="450" height="450" alpha="97">'
                 f'<Transform target="alpha" value="({on}?242:97)"/>'
                 f'<TextCircular centerX="{C}" centerY="{C}" width="{2 * rr}" height="{2 * rr}" startAngle="{sa:.2f}" endAngle="{ea:.2f}" direction="{d}">'
                 f'<Font family="inter_semibold" size="10" color="#ffffff" letterSpacing="0.24">{name}</Font></TextCircular></PartText>')
    # the "now" tick (2026)
    x1, y1 = pt(NOWA, R - 9)
    x2, y2 = pt(NOWA, R + 9)
    s.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="191">'
             f'<Line startX="{f1(x1)}" startY="{f1(y1)}" endX="{f1(x2)}" endY="{f1(y2)}"><Stroke color="#ffffff" thickness="1.5"/></Line></PartDraw>')
    # the ruby: rotates with the time (a quarter degree per minute)
    s.append(f'<PartDraw x="0" y="0" width="450" height="450" pivotX="0.5" pivotY="0.5">'
             f'<Transform target="angle" value="{I}/4"/>'
             f'<Ellipse x="{C - 8}" y="{C - R - 8}" width="16" height="16">'
             f'<Fill color="#9b111e"><RadialGradient centerX="{C + 3}" centerY="{C - R - 3}" radius="12" '
             f'colors="#ffd4475a #ff9b111e #ff45070d" positions="0 0.45 1"/></Fill>'
             f'<Stroke color="#fff4ead8" thickness="2"/></Ellipse></PartDraw>')
    s.append('</Group>')
    return '\n'.join(s)


def year():
    """The year: centred number, small muted AD hanging to its left on the baseline.
    Cormorant digits are made equal-width (0.491 em), so the number's width depends only on the digit count."""
    size, top = 112, 146 - 56
    adv = 0.491 * size + 0.01 * size                   # digit advance plus the simulator's letter-spacing
    digits = f'(({YEAR}>999)?4:(({YEAR}>99)?3:(({YEAR}>9)?2:1)))'
    ad_size = 0.15 * size
    ad_w = 34                                          # box for "AD", right-aligned
    ad_x = f'({C}-{digits}*{adv:.2f}/2-{ad_size * .6:.1f}-{ad_w})'
    return f'''<Group name="year" x="0" y="0" width="450" height="450">
<PartText x="0" y="{top}" width="450" height="{size + 20}">
<Text align="CENTER"><Font family="cormorant_garamond_semibold" size="{size}" color="#fff2e4cf">
<Transform target="color" value="{drift('ink')}"/>
<Template>%d<Parameter expression="{YEAR}"/></Template></Font></Text>
<Variant mode="AMBIENT" target="alpha" value="200"/>
</PartText>
<PartText x="0" y="{round(top + size * .72)}" width="{ad_w}" height="24" alpha="115">
<Transform target="x" value="{ad_x}"/>
<Text align="END"><Font family="inter_medium" size="{ad_size:.1f}" color="#fff2e4cf" letterSpacing="0.12">
<Transform target="color" value="{drift('ink')}"/>AD</Font></Text>
</PartText>
</Group>'''


def chord(y0, y1):
    r = FRIEZE_R - FRIEZE_W - CLEAR
    dy = max(abs(y0 - C), abs(y1 - C))
    return min(340, 2 * math.sqrt(max(0, r * r - dy * dy)))


def event_text():
    """Two lines of fixed sample text, each as wide as the frieze allows at its height.
    On the real face the companion app will break the text into lines and send them."""
    size, lh = 20, 26
    top = 226 + lh / 2                                  # two lines centred in the three-line block
    lines = ['First test of the History Clock', 'on a real Galaxy Watch Ultra']
    s = ['<Group name="event" x="0" y="0" width="450" height="450">']
    for n, t in enumerate(lines):
        y = top + n * lh
        w = chord(y, y + lh)
        s.append(f'<PartText x="{round(C - w / 2)}" y="{round(y)}" width="{round(w)}" height="{lh}">'
                 f'<Text align="CENTER" maxLines="1"><Font family="inter_medium" size="{size}" color="#fff2e4cf">'
                 f'<Transform target="color" value="{drift("ink")}"/>{sx.escape(t)}</Font></Text>'
                 f'<Variant mode="AMBIENT" target="alpha" value="180"/></PartText>')
    s.append('</Group>')
    return '\n'.join(s)


def pill():
    """Day and date in a pill at 6 o'clock, its lower corners against the clearance line."""
    w, h = 100, 34
    r = FRIEZE_R - FRIEZE_W - CLEAR
    rc, cx = h / 2, w / 2 - h / 2
    bottom = C + math.sqrt((r - rc) ** 2 - cx ** 2) + rc - 2
    y = bottom - h
    return f'''<Group name="pill" x="0" y="0" width="450" height="450">
<Variant mode="AMBIENT" target="alpha" value="0"/>
<PartDraw x="{round(C - w / 2)}" y="{round(y)}" width="{w}" height="{h}">
<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{h / 2}" cornerRadiusY="{h / 2}">
<Fill color="#52000000"/><Stroke color="#29ffffff" thickness="1"/></RoundRectangle>
</PartDraw>
<PartText x="{round(C - w / 2)}" y="{round(y + 8)}" width="{w}" height="20">
<Text align="CENTER"><Font family="inter_semibold" size="13" color="#fff2e4cf" letterSpacing="0.08">
<Transform target="color" value="{drift('ink')}"/>
<Upper><Template>%s %d<Parameter expression="[DAY_OF_WEEK_S]"/><Parameter expression="[DAY]"/></Template></Upper></Font></Text>
</PartText>
</Group>'''


VERSION = '0.3'


def build_tag():
    """Tiny build number under the pill, so we always know which build the watch is running (development only)."""
    return (f'<PartText x="200" y="392" width="50" height="14" alpha="90"><Variant mode="AMBIENT" target="alpha" value="0"/>'
            f'<Text align="CENTER"><Font family="inter_medium" size="9" color="#ffffff">v{VERSION}</Font></Text></PartText>')


def watchface():
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!-- GENERATED by clock/tools/make_watchface.py: do not edit by hand. History Clock v{VERSION}. -->
<WatchFace width="450" height="450">
<Metadata key="CLOCK_TYPE" value="DIGITAL"/>
<Metadata key="PREVIEW_TIME" value="18:09:30"/>
<Scene backgroundColor="#ff000000">
{background()}
{frieze()}
{seconds_glow()}
{era_ring()}
{year()}
{event_text()}
{pill()}
{build_tag()}
</Scene>
</WatchFace>
'''


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(watchface())
    print('wrote', os.path.relpath(OUT), os.path.getsize(OUT), 'bytes')

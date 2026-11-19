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


# The nine friezes, one per sub-period (as in the simulator), each fading into the next over the
# last FADE minutes before the change. They are drawn by the simulator's own pattern code and
# saved as images (clock/tools/render_friezes.py): Watch Face Format has no free-form paths.
# White images, tinted with the period's frieze colour, which drifts like the background.
PERIODS = [(0, 'laurel'), (200, 'meander'), (330, 'tesserae'), (600, 'knotwork'), (1100, 'tracery'),
           (1500, 'starchart'), (1800, 'gears'), (1900, 'blueprint'), (2027, 'orbits')]
FADE = 10


def period_alpha(n, full=255):
    """Alpha of period n's frieze: full inside its years, fading out over the last FADE minutes
    before the next period while that one fades in (as in the simulator)."""
    s = idx(PERIODS[n][0])
    e = idx(PERIODS[n + 1][0]) if n + 1 < len(PERIODS) else 99999
    f1_ = FADE + 1
    # fading in during the previous period's last FADE minutes
    fin = f'({full}*(1-({s}-{I})/{f1_}))' if n > 0 else '0'
    fout = f'({full}*(({e}-{I})/{f1_}))'
    return (f'(({s}>{I})?(({I}>={s - FADE})?{fin}:0):'
            f'(({e}>{I})?((({I})>={e - FADE})?{fout}:{full}):0))')


def friezes():
    s = ['<Group name="friezes" x="0" y="0" width="450" height="450">',
         '<Variant mode="AMBIENT" target="alpha" value="0"/>']
    for n, (yr, key) in enumerate(PERIODS):
        s.append(f'<PartImage x="0" y="0" width="450" height="450" alpha="0" tintColor="#ffffffff">'
                 f'<Transform target="alpha" value="{period_alpha(n)}"/>'
                 f'<Transform target="tintColor" value="{drift("pat")}"/>'
                 f'<Image resource="frieze_{key}"/></PartImage>')
    s.append('</Group>')
    return '\n'.join(s)


def seconds_glow():
    """A light travelling once round the frieze every minute, lighting the ornament itself:
    bright arc segments with a fading tail, masked by full-strength copies of the friezes."""
    fo, fi = FRIEZE_R, FRIEZE_R - FRIEZE_W
    mid, thick = (fo + fi) / 2, FRIEZE_W + 6
    head = '([SECOND]*6+[MILLISECOND]*0.006)'
    tail, seg = 100, 5
    mask = []
    for n, (yr, key) in enumerate(PERIODS):
        mask.append(f'<PartImage x="0" y="0" width="450" height="450" alpha="0">'
                    f'<Transform target="alpha" value="{period_alpha(n)}"/>'
                    f'<Image resource="frieze_{key}_mask"/></PartImage>')
    light = []
    for n in range(360 // seg):
        a = n * seg
        lag = f'(({head}-{a}+360)%360)'
        alpha = f'(({tail}>{lag})?(235*(1-{lag}/{tail})*(1-{lag}/{tail})):0)'
        light.append(f'<PartDraw x="0" y="0" width="450" height="450" alpha="0">'
                     f'<Transform target="alpha" value="{alpha}"/>'
                     f'<Arc centerX="{C}" centerY="{C}" width="{2 * mid}" height="{2 * mid}" startAngle="{a}" endAngle="{a + seg + 0.5}">'
                     f'<Stroke color="#ffffffff" thickness="{thick}"/></Arc></PartDraw>')
    return ('<Group name="seconds_glow" x="0" y="0" width="450" height="450">'
            '<Variant mode="AMBIENT" target="alpha" value="0"/>'
            '<Group name="glow_mask" x="0" y="0" width="450" height="450" renderMode="MASK">' + ''.join(mask) + '</Group>'
            '<Group name="glow_light" x="0" y="0" width="450" height="450" renderMode="SOURCE">' + ''.join(light) + '</Group>'
            '</Group>')


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
        rr = 203 if low else 191
        if low:
            sa, ea, d = a2 - 1, a1 + 1, 'COUNTER_CLOCKWISE'
        else:
            sa, ea, d = a1 + 1, a2 - 1, 'CLOCKWISE'
        s.append(f'<PartText x="0" y="0" width="450" height="450" alpha="97">'
                 f'<Transform target="alpha" value="({on}?242:97)"/>'
                 f'<TextCircular centerX="{C}" centerY="{C}" width="{2 * rr}" height="{2 * rr}" startAngle="{sa:.2f}" endAngle="{ea:.2f}" direction="{d}">'
                 f'<Font family="inter_semibold" size="13" color="#ffffff" letterSpacing="0.18">{name}</Font></TextCircular></PartText>')
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
    ad_size = 0.17 * size
    ad_w = 44                                          # box for "AD", right-aligned
    ad_x = f'({C}-{digits}*{adv:.2f}/2-{ad_size * .6:.1f}-{ad_w})'
    return f'''<Group name="year" x="0" y="0" width="450" height="450">
<PartText x="0" y="{top}" width="450" height="{size + 20}">
<Text align="CENTER"><Font family="cormorant_garamond_semibold" size="{size}" color="#fff2e4cf">
<Transform target="color" value="{drift('ink')}"/>
<Template>%d<Parameter expression="{YEAR}"/></Template></Font></Text>
<Variant mode="AMBIENT" target="alpha" value="200"/>
</PartText>
<PartText x="0" y="{round(top + size * .72)}" width="{ad_w}" height="28" alpha="150">
<Transform target="x" value="{ad_x}"/>
<Text align="END"><Font family="inter_medium" size="{ad_size:.1f}" color="#fff2e4cf" letterSpacing="0.12">
<Transform target="color" value="{drift('ink')}"/>AD</Font></Text>
</PartText>
</Group>'''


EVENT_SIZE, EVENT_TOP, MAX_LINES = 22, 222, 3     # 22 px (was 20): larger for legibility on the wrist
LH = EVENT_SIZE * 1.3


def chord(y0, y1):
    """Widest centred line between heights y0 and y1 that stays inside the clearance line."""
    r = FRIEZE_R - FRIEZE_W - CLEAR
    dy = max(abs(y0 - C), abs(y1 - C))
    return min(400, 2 * math.sqrt(max(0, r * r - dy * dy)))


_FONT = None


def text_width(t, size):
    global _FONT
    if _FONT is None:
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(HERE, '..', 'watchface', 'watchface', 'src', 'main', 'res', 'font', 'inter_medium.ttf'))
        _FONT = (f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm)
    cm, hm, upm = _FONT
    return sum(hm[cm.get(ord(ch), cm[ord('?')])][0] for ch in t) / upm * size


def layout_text(t):
    """Up to three lines, each as wide as the frieze allows at its height; the fewest lines that fit,
    breaks balanced between them; shorter texts centred in the three-line block (as in the simulator).
    The companion app will do the same on the watch."""
    words = t.split()
    for k in range(1, MAX_LINES + 1):
        off = (MAX_LINES - k) * LH / 2
        slots = [(EVENT_TOP + off + j * LH, chord(EVENT_TOP + off + j * LH, EVENT_TOP + off + (j + 1) * LH)) for j in range(k)]
        best = None

        def cuts(start, j, acc):
            nonlocal best
            if j == k - 1:
                line = ' '.join(words[start:])
                if not line or text_width(line, EVENT_SIZE) > slots[j][1]:
                    return
                parts = acc + [line]
                fill = [text_width(x, EVENT_SIZE) / slots[n][1] for n, x in enumerate(parts)]
                m = sum(fill) / len(fill)
                cost = sum((x - m) ** 2 for x in fill)
                if best is None or cost < best[0]:
                    best = (cost, parts)
                return
            for c in range(start + 1, len(words) - (k - 1 - j) + 1):
                line = ' '.join(words[start:c])
                if text_width(line, EVENT_SIZE) > slots[j][1]:
                    break
                cuts(c, j + 1, acc + [line])
        cuts(0, 0, [])
        if best:
            return [(slots[n][0], slots[n][1], line) for n, line in enumerate(best[1])]
    raise ValueError('text does not fit in three lines: ' + t)


SAMPLE = 'Construction of the Taj Mahal begins'          # fixed sample until the companion app sends real events


def event_text():
    s = ['<Group name="event" x="0" y="0" width="450" height="450">']
    for y, w, line in layout_text(SAMPLE):
        s.append(f'<PartText x="{round(C - w / 2)}" y="{round(y)}" width="{round(w)}" height="{round(LH) + 2}">'
                 f'<Text align="CENTER" maxLines="1"><Font family="inter_medium" size="{EVENT_SIZE}" color="#fff2e4cf">'
                 f'<Transform target="color" value="{drift("ink")}"/>{sx.escape(line)}</Font></Text>'
                 f'<Variant mode="AMBIENT" target="alpha" value="180"/></PartText>')
    s.append('</Group>')
    return '\n'.join(s)


PILL_W, PILL_H = 124, 42                                  # 25% larger than in v0.3


def pill_box():
    r = FRIEZE_R - FRIEZE_W - CLEAR
    rc, cx = PILL_H / 2, PILL_W / 2 - PILL_H / 2
    bottom = C + math.sqrt((r - rc) ** 2 - cx ** 2) + rc - 2
    return C - PILL_W / 2, bottom - PILL_H


def pill():
    """Day and date in a pill at 6 o'clock, its lower corners against the clearance line."""
    x, y = pill_box()
    w, h = PILL_W, PILL_H
    return f'''<Group name="pill" x="0" y="0" width="450" height="450">
<Variant mode="AMBIENT" target="alpha" value="0"/>
<PartDraw x="{round(x)}" y="{round(y)}" width="{w}" height="{h}">
<RoundRectangle x="0" y="0" width="{w}" height="{h}" cornerRadiusX="{h / 2}" cornerRadiusY="{h / 2}">
<Fill color="#52000000"/><Stroke color="#29ffffff" thickness="1"/></RoundRectangle>
</PartDraw>
<PartText x="{round(x)}" y="{round(y + 10)}" width="{w}" height="24">
<Text align="CENTER"><Font family="inter_semibold" size="16" color="#fff2e4cf" letterSpacing="0.08">
<Transform target="color" value="{drift('ink')}"/>
<Upper><Template>%s %d<Parameter expression="[DAY_OF_WEEK_S]"/><Parameter expression="[DAY]"/></Template></Upper></Font></Text>
</PartText>
</Group>'''


VERSION = '0.4'


def build_tag():
    """Build number just above the pill, readable, so we know which build the watch runs (development only)."""
    x, y = pill_box()
    return (f'<PartText x="185" y="{round(y - 22)}" width="80" height="18" alpha="130"><Variant mode="AMBIENT" target="alpha" value="0"/>'
            f'<Text align="CENTER"><Font family="inter_medium" size="13" color="#ffffff">v{VERSION}</Font></Text></PartText>')


def watchface():
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!-- GENERATED by clock/tools/make_watchface.py: do not edit by hand. History Clock v{VERSION}. -->
<WatchFace width="450" height="450">
<Metadata key="CLOCK_TYPE" value="DIGITAL"/>
<Metadata key="PREVIEW_TIME" value="18:09:30"/>
<Scene backgroundColor="#ff000000">
{background()}
{friezes()}
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

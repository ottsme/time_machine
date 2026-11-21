#!/usr/bin/env python3
"""First quick cleanup of the English dial texts (21 Nov 2026), done by Claude at Ott's request.

Not the real editorial review: only clear fixes.
  - broken words from v1's manual hyphenation joined again ("Constanti-nople" -> "Constantinople")
  - stray dashes and separators tidied
  - spelling mistakes
  - the factual errors already listed in the brief, plus a few more that are clearly wrong
  - texts shortened only where they don't fit three lines on the watch

Nothing is lost: the workbook keeps the v1 text of every changed row in a new column, and a
"Cleanup 2026-11-21" sheet lists every change with its reason. Unsure cases are flagged, not changed.

Usage: python3 cleanup_2026_11_21.py IN.xlsx OUT.xlsx
"""
import re
import sys
import openpyxl
from openpyxl.styles import Font, Alignment

# --- broken words from v1's manual line breaks (a hyphen typed where the line wrapped) ---
JOINS = {
    'perma-nent': 'permanent', 'him-self': 'himself', 'Mogunti-acum': 'Moguntiacum', 'threate-ned': 'threatened',
    'Völker-wanderung': 'Völkerwanderung', 'Dio-cletian': 'Diocletian', 'dedi-cated': 'dedicated',
    'histori-cally': 'historically', 'Cons-tantinople': 'Constantinople', 'Meso-potamia': 'Mesopotamia',
    'Constanti-nople': 'Constantinople', 'Constani-nople': 'Constantinople', 'consoli-dates': 'consolidates',
    'blee-ding': 'bleeding', 'intro-duces': 'introduces', 'sur-renders': 'surrenders', 'king-dom': 'kingdom',
    'forti-fications': 'fortifications', 'Visigoth-orum': 'Visigothorum', 'Charle-magne': 'Charlemagne',
    'govern-ment': 'government', 'Byzan-tine': 'Byzantine', 'assassi-nated': 'assassinated', 'Roma-na': 'Romana',
    'Rüstrin-gen': 'Rüstringen', 'Theo-dora': 'Theodora', 'Leka-penos': 'Lekapenos', 'Cons-tantine': 'Constantine',
    'beco-mes': 'becomes', 'super-nova': 'supernova', 'recor-ded': 'recorded', 'con-quers': 'conquers',
    'collap-ses': 'collapses', 'Hartha-cnut': 'Harthacnut', 'Scandi-navian': 'Scandinavian', 'Hard-rada': 'Hardrada',
    'indepen-dent': 'independent', 'strong-hold': 'stronghold', 'prae-decessores': 'praedecessores',
    'correc-tions': 'corrections', 'ex-communicated': 'excommunicated', 'app-roaching': 'approaching',
    'inter-actions': 'interactions', 'Ban-quet': 'Banquet', 'Lithu-anian': 'Lithuanian', 'Lithu-ania': 'Lithuania',
    'Geno-ese': 'Genoese', 'Zee-land': 'Zeeland', 'establish-ed': 'established', 'mari-time': 'maritime',
    'proporti-one': 'proportione', 'Grammati-cus': 'Grammaticus', 'Massa-chusetts': 'Massachusetts',
    'dis-solves': 'dissolves', 'Parlia-ment': 'Parliament', 'Brobding-nag': 'Brobdingnag',
    'billio-naire': 'billionaire', 'Ribben-trop': 'Ribbentrop', 'presi-dent': 'president',
    'black-mails': 'blackmails', 'Confine-ment': 'Confinement', 'unemp-loyed': 'unemployed',
}

# --- whole-text changes: year -> (new text, kind, note) ---
FIX = {
    9: ('Arminius defeats 3 Roman legions in Teutoburg Forest', 'spelling', 'Teutoborg -> Teutoburg'),
    27: ('John baptises Jesus in River Jordan', 'spelling', 'babtises'),
    30: ('Crucifixion of Jesus (probable; trad. date 33)', 'spelling', 'Crucification'),
    103: ('Roman army builds 1st permanent Danube bridge', 'dash', '"1. perma-nent"'),
    136: ('Hadrian expels Jews from Galilee', 'spelling', 'Galilea'),
    138: ('† Hadrian, Antoninus Pius succeeds', 'spelling', 'Antoninius; dropped "-> M. Aurelius" (unclear)'),
    156: ('Montanism spreads in Phrygia (Anatolia)', 'spelling', 'Frygia'),
    159: ('Limes moved 25–30 km east on the Upper Rhine', 'spelling', 'Rhein -> Rhine'),
    222: ('Elagabalus killed by Praetorians, damnatio memoriae', 'tidy', '"† by", "+"'),
    223: ('Praetorian Guards kill their prefect Ulpian', 'tidy', '"†" used as a verb. FLAG: duplicate of 228; Ulpian was killed in 223 or 228'),
    235: ('Maximinus Thrax: era of "barracks emperors" begins', 'spelling', 'barracs'),
    301: ('Diocletian regulates prices; inflation rises', 'spelling', 'infation'),
    315: ('Crucifixion banned as punishment in Rome', 'spelling', 'Crucification'),
    318: ('Constantine the Great given title Britannicus Maximus', 'spelling', 'Brittanicus'),
    337: ('† Constantine the Great, empire split among 3 sons', 'shortened', 'too long for three lines (sons: Constantine II, Constantius II, Constans)'),
    952: ('Constantine VII writes "De Administrando Imperio"', 'shortened', 'too long for three lines'),
    1320: ('Scots sign the Declaration of Arbroath', 'shortened', 'too long for three lines'),
    535: ('Eruption of Krakatoa → years of climate change', 'tidy', 'FLAG: cause of the 535–536 climate event is disputed; Krakatoa is one theory'),
    610: ('Official language of Eastern Empire: Latin → Greek', 'tidy', '"->"'),
    616: ('Judea and Galilee become Persian provinces', 'spelling', 'Galilea'),
    619: ("Muhammad's wife Khadija dies: the Year of Sorrow", 'tidy', '"->"'),
    622: ('Hegira: Muhammad from Mecca to Medina', 'tidy', '" - "'),
    644: ("Caliph Uthman begins codifying the Qur'an text", 'spelling', 'Uthmanuran. FLAG: the Uthmanic codex is usually dated c. 650–653'),
    716: ('Umayyad campaign against Constantinople', 'spelling', 'campain'),
    718: ('Battle of Soissons: Charles Martel → dux Francorum', 'tidy', '"->"'),
    741: ('† Charles Martel, lands divided between his sons', 'tidy', '"÷"'),
    806: ('Divisio Regnorum: Charlemagne divides empire among 3 sons', 'tidy', '"÷", "btwn"'),
    835: ("Pope Gregory IV sets 1 November as All Saints' Day", 'tidy', '"1. Nov."'),
    840: ('1st permanent Viking settlements in Ireland', 'tidy', '"1. Viking permanent". FLAG: Dublin (841) is the usual date'),
    949: ('Byzantine navy tries to reconquer Crete, fails', 'spelling', 'reconqure'),
    950: ('Fire lance in China: oldest gunpowder weapon', 'tidy', '" - "'),
    951: ('Abd al-Rahman of Córdoba conquers Tangiers', 'spelling', 'al-Rahmad'),
    953: ('Roman bridge over Rhine, built in 310, collapses', 'spelling', 'Rhein'),
    1034: ("Russian Church accepts Constantinople's authority", 'shortened', 'spelling (Constaninople patriarchy) and too long for three lines'),
    1049: ('2nd Council of Reims condemns simony', 'spelling', 'condems simonia'),
    1059: ('College of Cardinals: sole voters in papal conclave', 'tidy', '" - "'),
    1135: ('Anarchy begins in England, lasts till 1154', 'fact', 'was "till 1553": the Anarchy ended in 1154'),
    1143: ('City of Lübeck founded, capital of Hanseatic League', 'spelling', 'Lubeck'),
    1215: ('King John seals Magna Carta, limiting royal power', 'fact', 'brief: it was sealed, not signed'),
    1316: ('Great Famine of 1315–1317 at its peak', 'dash', '"1315- -1317"'),
    1327: ('Hangzhou–Beijing canal, over 1,800 km, completed', 'dash', '"--". FLAG: completion date of the Grand Canal to Beijing (1293?) to check'),
    1351: ("Edward III's Treason Act, still in force today", 'spelling', '"in in"'),
    1418: ("Siege of Rouen begins in the Hundred Years' War", 'dash', '"100- Years\'-War"'),
    1425: ('Old University of Leuven founded', 'spelling', 'Leuwen (Old) University'),
    1439: ('Council of Florence unites Latin and Greek Churches', 'new', 'v1 cell held only "58" (garbled). New text: the 1439 union decree (Laetentur Caeli); short-lived'),
    1629: ("Charles I dissolves Parliament → 11 Years' Tyranny", 'dash', '"dis-solves Parlia-ment, ->"'),
    1658: ('† Oliver Cromwell, son Richard → Lord Protector', 'tidy', '"->"'),
    1714: ('Russia occupies Finland: the Great Wrath', 'fact', 'was "completes annexation of Finland": Finland was occupied 1714–1721 and annexed only in 1809'),
    1721: ('Peter I proclaimed Emperor of All Russia', 'spelling', "All Russia's"),
    1730: ('R.A.F. de Réaumur develops scale 0°–80°', 'dash', '"0° - 80°"'),
    1741: ('Handel composes Messiah in 24 days', 'fact', 'was "Anders Celsius develops Centigrade scale": Celsius proposed his scale in 1742. To reserve, for 1742'),
    1826: ('Lobachevsky develops non-Euclidean geometry', 'spelling', 'Euclidian'),
    1840: ("Britain's Penny Black: world's 1st postage stamp", 'tidy', '" - "'),
    1928: ('Alexander Fleming discovers penicillin', 'spelling', 'peniccilin'),
    2109: ('2009 time capsule at Rutgers Uni. opened', 'spelling', 'Opened'),
    2128: ("2000 yrs from completion of Hadrian's Wall", 'spelling', 'Hadrian Wall'),
    2134: ("Halley's Comet returns", 'fact', 'was "150 yrs from 1st in vitro child 1984": the first IVF baby was born in 1978. Halley\'s next-but-one return is in 2134'),
    2136: ("300 yrs from end of Darwin's Beagle voyage (1836)", 'fact', 'was "Halley\'s Comet returns again": that return is in 2134'),
    2148: ('Triple conjunction Mars–Saturn', 'dash', '" - "'),
    2211: ("250 yrs from Yuri Gagarin's flight in 1961", 'spelling', 'fom'),
    2215: ('Magna Carta 1000 (1215)', 'fact', 'was "750 yrs ... 1465": 2215 is the 1000th anniversary'),
    2230: ('2200 yrs from probable crucifixion of Jesus', 'spelling', 'crucification'),
    2231: ("Cambridge University's royal charter 1000 (1231)", 'fact', 'was "University of Cambridge 1000": founded 1209, so its 1000th is 2209. 2231 fits the 1231 charter'),
    2235: ("Schrödinger's cat 300 (1935)", 'dash', '" - "'),
    2241: ("500 yrs from Handel's Messiah (1741)", 'fact', 'was "500 yrs from invention of Centigrade scale": Celsius 1742, so that 500th is 2242'),
    2242: ('300 yrs from encirclement of German 6th Army at Stalingrad', 'fact', 'was "sack of German 9th Army": it was the 6th Army, encircled Nov 1942, surrendered 1943'),
    2249: ('300 yrs from Israel joining the UN (1949)', 'fact', 'was "State of Israel 300 (1949)": Israel was declared in 1948'),
    2325: ('Mein Kampf and The Great Gatsby 400 (1925)', 'fact', 'was "- 500": 2325 is the 400th'),
    2336: ('350 yrs from Chernobyl catastrophe in 1986', 'spelling', 'catastrophy'),
    2352: ('David Hasselhoff 400 (1952)', 'spelling', 'Hasselhof'),
}

# --- unchanged but worth checking in the real review ---
FLAGS = {
    42: 'duplicate of 34 (Paul\'s conversion)',
    228: 'duplicate of 223 (Ulpian)',
    302: 'the Great Persecution began in 303 (see 303)',
    1153: 'duplicate of 340 (largest city)',
    1723: '"abolishes slavery": household slavery merged into serfdom; wording to check',
    1742: 'Celsius proposed his scale in 1742; the current text (Izmir fire) to check',
    2209: 'next perihelion of Halley after 2134 is uncertain (2209/2210?)',
    2236: 'BBC: Company 1922, Corporation 1927, TV service 1936; "BBC 300 (1936)" to check',
    2319: 'kick scooter invented 1819? to check',
}


def clean(t):
    t = str(t).replace('-\n', '-').replace('\n', ' ')
    return re.sub(r'\s{2,}', ' ', t).strip()


def main(src, dst):
    wb = openpyxl.load_workbook(src)
    ws = wb['WF Tekstid ENG']
    ws.cell(2, 5, 'Text v1 (before 21 Nov 2026 cleanup)').font = Font(bold=True)
    ws.cell(2, 6, 'Cleanup note').font = Font(bold=True)
    log = wb.create_sheet('Cleanup 2026-11-21')
    log.append(['Year', 'Kind', 'v1 text', 'New text', 'Note'])
    for c in log[1]:
        c.font = Font(bold=True)
    for row in ws.iter_rows(min_row=3):
        if row[0].value is None or row[1].value is None:
            continue
        y = int(str(row[0].value))
        old = str(row[1].value)
        new = clean(old)
        kind, note = None, ''
        for a, b in JOINS.items():
            if a in new:
                new = new.replace(a, b)
                kind, note = 'dash', f'broken word joined ({a})' if not note else note + f', {a}'
        if y in FIX:
            new, kind, note = FIX[y]
        if new != clean(old) or y in FIX:
            row[1].value = new
            ws.cell(row[0].row, 5, old)
            ws.cell(row[0].row, 6, f'{kind}: {note}')
            log.append([f'{y:04d}', kind, clean(old), new, note])
        elif '\n' in old:
            row[1].value = new          # v1 line breaks joined, text otherwise unchanged
        if y in FLAGS:
            ws.cell(row[0].row, 6, (ws.cell(row[0].row, 6).value or '') + f' FLAG: {FLAGS[y]}')
            log.append([f'{y:04d}', 'flag', clean(old), '', FLAGS[y]])
    log.column_dimensions['C'].width = 55
    log.column_dimensions['D'].width = 55
    log.column_dimensions['E'].width = 80
    for r in log.iter_rows(min_row=2):
        for c in r:
            c.alignment = Alignment(wrap_text=True, vertical='top')
    wb.save(dst)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

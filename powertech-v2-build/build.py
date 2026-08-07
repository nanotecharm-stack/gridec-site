# -*- coding: utf-8 -*-
"""Assemble Gridec one-page (EN+HY) from shell.html + exact site texts."""
import base64, io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
# The site repo (a worktree) supplies the real fonts for the base64 preview build and
# receives the deploy pair. PT_SITE points at it; by default it is the sibling `assets`.
SITE = os.environ.get('PT_SITE') or os.path.join(HERE, '..', 'assets')
FONTS = os.path.join(SITE, 'fonts')
IMGS = os.path.join(HERE, 'img')

def b64(path, mime):
    with open(path, 'rb') as f:
        return 'data:' + mime + ';base64,' + base64.b64encode(f.read()).decode()

def font_face(fam, weight, fn):
    return ("@font-face{font-family:'%s';font-weight:%s;font-display:swap;"
            "src:url(%s) format('woff2');}"
            % (fam, weight, b64(os.path.join(FONTS, fn), 'font/woff2')))

FF_EN = '\n'.join([
    font_face('Big Shoulders Display', 700, 'big-shoulders-display-700-latin.woff2'),
    font_face('Archivo', 400, 'archivo-400-latin.woff2'),
    font_face('Archivo', 600, 'archivo-600-latin.woff2'),
    font_face('Martian Mono', 600, 'martian-mono-600-latin.woff2'),
])
# Departure Mono, пиксельный, SIL OFL — шрифт показаний. Вес объявлен диапазоном,
# хотя начертание одно: иначе на элементах с 600 браузер подделает жир и размажет
# пиксельные штрихи.
FF_DEP = (
    "@font-face{font-family:'Departure Mono';font-weight:100 900;font-display:swap;"
    "src:url(%s) format('woff2');}"
    % b64(os.path.join(FONTS, 'departure-mono.woff2'), 'font/woff2'))

# Правила показаний. Кегль 11 — сетка шрифта; ниже он теряет штрихи, выше мылится.
# Трекинг вдвое меньше прежнего: прежний рассчитан на узкий Martian Mono.
READOUT_EN = """
/* ============ ПОКАЗАНИЯ ============
   Пиксельный шрифт достаётся только тому, что является показанием прибора: номерам,
   счётчику и значениям. Слова остаются на прежнем — на длинных строках пиксельная
   сетка бледнеет и теряет вес рядом с основным текстом. */
.cnt,.ixb,.ixp a .no,.rd,.mi .ix,.chsteps .n,.step .no,.list .n,.asg .no{
  font-family:'Departure Mono',monospace;font-size:11px;}
.cnt{letter-spacing:.11em;}
.ixb{letter-spacing:.05em;}
.ixp a .no,.mi .ix,.list .n,.asg .no{letter-spacing:.07em;}
.chsteps .n{letter-spacing:.09em;}
.step .no{letter-spacing:.08em;}
/* число и слово лежат в одном элементе — слово возвращается прежнему шрифту */
.ixb .sheet{font-family:%(mono)s;font-size:12px;letter-spacing:.1em;}
.rd>span:not(.st){font-family:%(mono)s;font-size:12px;}
"""

# На армянской странице — только цифровой слой: армянских букв у шрифта нет, поэтому
# кольцо остаётся на Arian AMU Serif, а в показании цифры берутся отдельно от слов.
READOUT_HY = """
/* ============ ПОКАЗАНИЯ ============
   Только цифры: армянского у пиксельного шрифта нет, слова остаются прежними. */
.cnt,.ixp a .no,.mi .ix,.chsteps .n,.step .no,.list .n,.asg .no,.rd b,.ixb b,.ixb em{
  font-family:'Departure Mono',monospace;font-size:11px;}
.cnt{letter-spacing:.11em;}
.ixp a .no,.mi .ix,.list .n,.asg .no{letter-spacing:.07em;}
.chsteps .n{letter-spacing:.09em;}
.step .no{letter-spacing:.08em;}
"""

MONO_EN = "'Martian Mono',monospace"
MONO_HY = "'Arian AMU Serif',Georgia,serif"

FF_HY = '\n'.join([
    font_face('Arian AMU', '400 500', 'arian-amu-400.woff2'),
    font_face('Arian AMU', '600 900', 'arian-amu-700.woff2'),
    font_face('Arian AMU Serif', '400 500', 'arian-amu-serif-400.woff2'),
    font_face('Arian AMU Serif', '600 900', 'arian-amu-serif-700.woff2'),
])

IMG_FILES = ['02_manufacturing_industrial_robot.jpg', '03_solar_power_plant.jpg',
             '06_healthcare_laboratory.jpg', '05_data_center.jpg',
             '04_commercial_building.jpg', '08_finance_investment.jpg']
def b64_small(path, maxw=1800, quality=82):
    """Вшитая копия снимка, уменьшенная до maxw.

    Самый крупный вывод фотографии — модалка отрасли, 880x385 CSS, то есть 1760 px при
    экране 2x. Оригиналы 2400 px в base64 дают около 8 МБ на страницу без видимой
    разницы. Деплойная сборка ссылается на файлы и получает полный размер. Без Pillow
    вшиваем как есть, чтобы сборка не падала.
    """
    try:
        from PIL import Image
    except ImportError:
        return b64(path, 'image/jpeg')
    im = Image.open(path)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


IMGD = {'IMG%d' % i: b64_small(os.path.join(IMGS, f)) for i, f in enumerate(IMG_FILES)}

def stats_html(items):
    return ''.join('<div class="stat"><b>%s</b><span>%s</span></div>' % (b, s) for b, s in items)

def steps_html(items):
    return ''.join('<div class="step"><div class="no">%s</div><h3>%s</h3><p>%s</p></div>' % (n, t, p)
                   for n, t, p in items)

def list_html(items):
    return ''.join('<div><span class="n">%02d</span><span>%s</span></div>' % (i + 1, x)
                   for i, x in enumerate(items))

def asg_html(items):
    return ''.join('<div class="card"><div class="hd"><span class="no">%s</span>'
                   '<span class="tag">%s</span></div><h3>%s</h3><p>%s</p></div>' % (n, tg, t, p)
                   for n, tg, t, p in items)

# Each parameter gets its own measurement signature. Drawn to the owner's sketches
# (2026-07-28) in the site's own hairline language: one stroke weight, currentColor for
# the structure and var(--brand) for the single accent, so every icon inherits the page
# palette and inverts on the dark plates. No gradients, no fills, nothing that needs a
# raster. They render at 52x34 CSS pixels, which is what settles most of the detail
# decisions below.
MEAS_ICONS = [
 # 01 voltage & current — three linked loops crossing one axis, the middle phase lit
 '<g fill="none" stroke="currentColor" stroke-width="1.1">'
 '<ellipse cx="13" cy="15" rx="6.6" ry="10.4"/><ellipse cx="31" cy="15" rx="6.6" ry="10.4"/></g>'
 '<ellipse cx="22" cy="15" rx="6.6" ry="10.4" fill="none" stroke="var(--brand)" stroke-width="1.4"/>'
 '<g stroke="currentColor" stroke-width="1.1" stroke-linecap="round" opacity=".7">'
 '<path d="M2.5 15h10"/><path d="M31.5 15h10"/></g>'
 '<path d="M19 15h6" stroke="var(--brand)" stroke-width="1.7" stroke-linecap="round"/>',
 # 02 harmonics — a decaying spectrum, the third order carrying the accent
 '<path d="M2 21h40" stroke="currentColor" stroke-width="1" opacity=".5"/>'
 '<g fill="none" stroke="currentColor" stroke-width="1">'
 '<rect x="8" y="4" width="3" height="19"/><rect x="13" y="7" width="3" height="16"/>'
 '<rect x="23" y="13" width="3" height="10"/><rect x="28" y="16" width="3" height="7"/>'
 '<rect x="33" y="18.4" width="3" height="4.6"/></g>'
 '<rect x="18" y="10" width="3" height="13" fill="var(--brand)"/>',
 # 03 flicker — the fluctuation held between two limit lines
 '<g stroke="currentColor" stroke-width="1" opacity=".38" stroke-dasharray="3 3">'
 '<path d="M4 8h36"/><path d="M4 22h36"/></g>'
 '<path d="M4 15c2 4 4 4 6 0s4-6 6 0 4 8 6 0 4-6 6 0 4 4 6 0" fill="none" stroke="currentColor" stroke-width="1.4"/>'
 '<path d="M4 15c2 4 4 4 6 0s4-6 6 0 4 8 6 0" fill="none" stroke="var(--brand)" stroke-width="1.4"/>',
 # 04 voltage dip — a smooth sag that recovers short of where it started,
 #    with the accent marking the depth it reached
 '<path d="M2 10c6 0 7 13 13 13s6-6 12-6 9 1 15 1" fill="none" stroke="currentColor" '
 'stroke-width="1.4" stroke-linecap="round"/>'
 '<path d="M12.5 23h9" stroke="var(--brand)" stroke-width="2.2" stroke-linecap="round"/>',
 # 05 unbalance — a star point whose lit phase runs long
 '<g stroke="currentColor" stroke-width="1.4" stroke-linecap="round">'
 '<path d="M22 15.5 13.5 21"/><path d="M22 15.5 30.5 21"/></g>'
 '<g fill="currentColor"><circle cx="13.5" cy="21" r="1.9"/><circle cx="30.5" cy="21" r="1.9"/></g>'
 '<path d="M22 15.5V4" stroke="var(--brand)" stroke-width="1.6" stroke-linecap="round"/>'
 '<circle cx="22" cy="4" r="2" fill="var(--brand)"/>'
 '<circle cx="22" cy="15.5" r="2.1" fill="currentColor"/>',
 # 06 power & energy — the area accumulated under the curve, closed by the accent
 '<path d="M2 24c8 0 10-13 18-13s10 8 22 4v9z" fill="currentColor" opacity=".14"/>'
 '<path d="M2 24c8 0 10-13 18-13s10 8 22 4" fill="none" stroke="currentColor" stroke-width="1.4"/>'
 '<path d="M2 24h40" stroke="var(--brand)" stroke-width="1.6"/>',
 # 07 events — a transient on a quiet line, flagged
 '<path d="M2 18h14l3-13 3.4 22 2.6-9h17" fill="none" stroke="currentColor" '
 'stroke-width="1.4" stroke-linejoin="round"/>'
 '<rect x="27" y="10.5" width="3" height="5.4" rx=".9" fill="var(--brand)"/>',
 # 08 risk indicators — NOT an electrical parameter: a trend read off the baseline
 #    whose latest point is flagged. This is the one card that draws a conclusion
 #    rather than a measurement, which is why its cell is marked (.mi-alt).
 '<g stroke="currentColor" stroke-width=".8" opacity=".26">'
 '<path d="M8 21v5"/><path d="M14 18v8"/><path d="M20 20v6"/><path d="M26 14v12"/>'
 '<path d="M32 16v10"/></g>'
 '<path d="M3 24 8 21 14 18 20 20 26 14 32 16 37 11" fill="none" stroke="currentColor" '
 'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
 '<g fill="currentColor"><circle cx="8" cy="21" r="1.4"/><circle cx="14" cy="18" r="1.4"/>'
 '<circle cx="20" cy="20" r="1.4"/><circle cx="26" cy="14" r="1.4"/><circle cx="32" cy="16" r="1.4"/></g>'
 '<circle cx="37" cy="11" r="2.5" fill="none" stroke="var(--brand)" stroke-width="1.6"/>'
 #    (the sketch's exclamation mark inside the triangle is dropped: at this size the
 #    notch would need the ground colour, which differs between the light and dark
 #    surfaces the grid can sit on, and a 1px sliver reads as dirt either way)
 '<path d="M37 1.4 40.1 6.8h-6.2z" fill="var(--brand)"/>',
]

def meas_html(items, alt=0):
    """`alt` = how many trailing cells are not electrical parameters. They get .mi-alt,
    which sets them apart from the measured quantities without inventing any copy."""
    out = []
    for i, label in enumerate(items):
        cls = 'mi mi-alt' if i >= len(items) - alt else 'mi'
        out.append('<div class="%s"><span class="ix">%02d</span>'
                   '<svg viewBox="0 0 44 30" aria-hidden="true">%s</svg>'
                   '<span class="lb2">%s</span></div>'
                   % (cls, i + 1, MEAS_ICONS[i % len(MEAS_ICONS)], label))
    return ''.join(out)

def chips_html(items):
    return ''.join('<span>%s</span>' % x for x in items)

def stages_html(items):
    # a real marker element: a generated one proved unreliable to verify
    return ''.join('<div class="p"><i class="mk"></i><div class="no">%s</div>'
                   '<p>%s</p></div>' % (t, p) for t, p in items)

# ---------------------------------------------------------------- EN
EN = {
 'LANG': 'en', 'TITLE': 'Gridec | Power Quality Monitoring',
 'FONTFACES': FF_EN + '\n' + FF_DEP,
 'READOUT': READOUT_EN % dict(mono=MONO_EN),
 'BODYFONT': "'Archivo','Helvetica Neue',Helvetica,Arial,sans-serif",
 'HEADFONT': "'Big Shoulders Display',sans-serif",
 'MONOFONT': MONO_EN,
 'NAVFONT': 'inherit',
 'HEADTT': 'text-transform:uppercase;', 'HEADLH': '.92', 'HEADLS': '.006em',
 'H1SIZE': 'clamp(48px,7.2vw,116px)', 'H2SIZE': 'clamp(30px,4.8vw,72px)',
 # Латинский код, а не «ՀԱՅ»: в EN-сборку вшита только латинская подрезка Martian
 # Mono, армянские буквы падали в системную подмену и выглядели чужеродно. Пара
 # переключателя заодно стала симметричной — на HY-странице стоит «EN».
 'LANG_HREF': './hy.html', 'LANG_LABEL': 'HY',
 'NAV_SERVICES': 'Services', 'NAV_INDUSTRIES': 'Industries', 'NAV_COMPANY': 'Company',
 'CTA': 'Describe the issue',
 'HERO_EYEBROW': 'POWER QUALITY MONITORING',
 'HERO_H1': 'See how your<br>electrical system<br><em>performs</em>',
 'HERO_P': 'Gridec monitors electrical parameters and power quality events while your system is operating. We interpret the recorded data and provide a clear engineering assessment.',
 'HERO_CTA2': 'How monitoring works',
 'RD_CAP': 'RMS VOLTAGE · 10-MIN TREND', 'RD_NOMINAL': 'NOMINAL',
 'WHY_H2': 'The event may be over before anyone can inspect it',
 'WHY_P': 'Some voltage events last only milliseconds or a few cycles. By the time the system is inspected, measured values may have returned to normal. Monitoring provides a time-stamped record of the event and the conditions around it.',
 'WHY_LINK': 'See where monitoring helps',
 'APP_H2': 'Where monitoring helps',
 'APP_P': 'Power quality problems are not limited to one sector. Monitoring is useful when electrical conditions affect equipment or operations, or when an engineering decision requires measured evidence.',
 'OTHER_T': 'Other Critical Electrical Systems',
 'OTHER_P': 'Do not see your sector here? Describe the issue and the equipment affected. Monitoring is defined by the technical question, not by the sector alone.',
 'SVC_EYEBROW': 'SERVICES', 'SVC_H2': 'Seven-day monitoring',
 'SVC_P1': 'Power quality data is recorded during actual operation and interpreted in the context of the issue being investigated.',
 'SVC_P2': 'The monitoring period is selected to obtain a representative record of operating conditions. A longer period may be recommended when the issue is intermittent or the operating cycle requires more time.',
 'SVC_STATS': stats_html([('7', 'typical diagnostic period'),
                          ('24/7', 'monitoring throughout the period'),
                          ('1', 'structured engineering report')]),
 'SVC_DISPLAY': 'Measured<br>under actual<br><i>load</i>',
 'SVC_STEPS': steps_html([
    ('01', 'Define the objective', 'We clarify what needs to be verified, the equipment involved and the decision the findings should support.'),
    ('02', 'Monitor in operation', 'Measurements are carried out while the electrical system operates under representative operating conditions.'),
    ('03', 'Deliver an engineering assessment', 'The findings are assessed in context and presented in a clear technical report, with conclusions supported by the recorded data and recommended next steps.')]),
 'SVC_LINK': 'See what monitoring can reveal',
 'REP_H2': 'A report built for technical decisions',
 'REP_P': 'The report separates measured facts from engineering interpretation and recommendations.',
 'REP_NOTE': 'Power quality parameters are measured using IEC 61000-4-30 Class S methods. Harmonic and interharmonic measurements are evaluated using IEC 61000-4-7 where applicable.',
 'REP_LIST': list_html(['Measurement scope and points', 'Monitoring period and operating context',
                        'Recorded events and trends', 'Engineering interpretation',
                        'Limitations of the available evidence', 'Recommended next steps']),
 'ASG_H2': 'Typical assignments',
 'ASG_P': 'Each assignment is shaped by the technical question and the evidence required.',
 'ASG_CARDS': asg_html([
    ('01', 'INCIDENTS', 'Incident Investigation', 'Assess whether equipment trips, alarms or process interruptions coincide with recorded electrical events.'),
    ('02', 'HANDOVER', 'Commissioning and Handover Assessment', 'Record electrical operating conditions to support acceptance, handover or end-of-warranty review.'),
    ('03', 'SOLAR', 'Solar PV Connection Assessment', 'Assess voltage conditions and inverter events at relevant points within the plant and at the point of connection.'),
    ('04', 'DUE DILIGENCE', 'Technical Due Diligence Measurements', 'Provide independent measurements of loading, power quality and observed operating constraints to support technical due diligence.')]),
 'MEA_H2': 'What we measure',
 'MEA_CHIPS': meas_html(['Voltage & Current', 'Harmonics & Interharmonics', 'Flicker',
                          'Voltage Dips', 'Unbalance', 'Power & Energy', 'Events',
                          'Risk Indicators'], alt=1),
 'CO_EYEBROW': 'COMPANY',
 'CO_H2': 'Measured data<br>Independent engineering assessment',
 'CO_P': 'Gridec was created to make electrical problems measurable. We record how electrical systems behave during operation and provide independent engineering assessments based on the recorded data. Gridec is based in Yerevan and works on-site across the region.',
 'CO_SUB': 'From on-site setup to engineering report',
 'CO_SUBP': 'One engineering lead oversees setup, recording and analysis.',
 'CO_STAGES': stages_html([
    ('01 · ON-SITE', 'Monitoring setup verified before recording'),
    ('02 · RECORDING', 'Electrical conditions recorded for the agreed period'),
    ('03 · ASSESSMENT', 'Findings interpreted in context and documented')]),
 'CT_H2': 'Start with what happened',
 'CT_P': 'Describe the event, the affected equipment and when it occurred or tends to occur. We will assess whether monitoring can answer the question and what scope is required.',
 'CT_CAP': 'RMS VOLTAGE · 10-MIN TREND', 'CT_NOM': 'NOMINAL', 'CT_DIP': 'VOLTAGE DIP · 180 MS',
 'FOOT_ADDR': 'Davtashen 1, 13-25, Yerevan 0058, Armenia',
 'IM_FINDLB': 'What the report can address',
 'F_H3': 'Describe the <i>electrical issue</i>',
 'F_INTRO': 'Tell us what happened, when it occurred or tends to occur, and which equipment is affected. We will assess whether monitoring can answer the question and what information is needed.',
 'F_CONTACT': 'Contact details',
 'F_NAME': 'Name', 'F_NAME_PH': 'Your name',
 'F_COMPANY': 'Company', 'F_COMPANY_PH': 'Company name',
 'F_EMAIL': 'Email', 'F_PHONE': 'Phone',
 'F_APP': 'Application',
 'F_WHAT': 'What happened?',
 'F_MSG_PH': 'Describe the trip, alarm, shutdown or recurring condition. Include approximate times, affected equipment and available error codes or logs.',
 'F_ATT': 'Attachments', 'F_ATT_OPT': '(optional)',
 'F_DROP1': 'Drop files here or click to browse',
 'F_DROP2': 'Single-line diagram, panel photo, alarm screenshot, inverter or UPS log, previous report.',
 'F_SIZE_ERR': 'Attachments exceed the 10 MB limit. Please remove some files.',
 'F_HINT0': 'Up to 10 MB total.',
 'F_FORM_ERR': 'Please fill in all fields: name, company, a valid email, phone and a short description.',
 'F_SEND': 'Send the details',
 'F_CONTACTLINE': 'sales@powertech.am · +374 41 00 00 14 · Davtashen 1, 13-25, Yerevan 0058 · Mon-Fri 09:00-18:00 (UTC+4)',
 'F_OK_T': 'Thank you.',
 'F_OK_P': 'We will review the information and contact you to clarify the measurement scope.',
 'F_CLOSE': 'Close',
}
EN_DATA = {
    # Кольцо величин в герое: номер, две строки названия, признак акцента.
    # Восьмая позиция — заключение, а не измерение, поэтому помечена.
    # Армянские термины взяты из словаря самой страницы, а не переведены заново.
    'ring': [['01', 'VOLTAGE', '& CURRENT', 0], ['02', 'HARMONICS', '', 0],
             ['03', 'FLICKER', '', 0], ['04', 'DIPS', '& SWELLS', 0],
             ['05', 'UNBALANCE', '', 0], ['06', 'POWER', '& ENERGY', 0],
             ['07', 'EVENTS', '', 0], ['08', 'RISK', 'READ', 1]],
 'canvasFont': '"Departure Mono",monospace',
 'rdNominal': 'NOMINAL', 'rdDip': 'VOLTAGE DIP · 180 MS',
 'incident': 'Incident',
 'seq': [['01', 'Normal operation'], ['02', 'Electrical event'], ['03', 'Equipment trip or alarm'],
         ['04', 'System returns to normal'], ['05', 'The event record remains available for analysis']],
 'viewDetails': 'View details',
 'hint1': ' file · ', 'hintN': ' files · ', 'hintSuf': ' of 10 MB', 'hint0': 'Up to 10 MB total.',
 'appTypes': ['Manufacturing', 'Solar PV', 'Healthcare or laboratory',
              'Data center or IT infrastructure', 'Commercial building',
              'Investment and Technical Review', 'Other'],
 'cards': [
  {'num': '01', 'title': 'Manufacturing', 'img': 'IMG0',
   'p1': 'Backup generation is designed for interruptions on a different time scale. A short voltage dip may affect equipment before transfer occurs, so the event must be recorded while it happens.',
   'findings': ['Timestamp, duration, minimum RMS voltage and affected phases of recorded dips.',
                'Voltage unbalance and current loading relevant to motor operation.',
                'Whether reactive power or harmonic distortion requires further engineering review.'],
   'statLabel': 'Technical note',
   'statText': 'Voltage sags and momentary interruptions can trip electronic and electromechanical devices and stop production lines.',
   'statSource': 'Source: EPRI'},
  {'num': '02', 'title': 'Solar PV', 'img': 'IMG1',
   'p1': 'Voltage rise can reflect the interaction of plant output, internal impedance and upstream network conditions. Measurements at relevant points can help distinguish plant-side from network-side factors.',
   'findings': ['Voltage conditions during inverter disconnection or active-power limitation.',
                'Voltage and harmonic distortion against applicable connection requirements.',
                'Independent measurement evidence for commissioning or EPC review.'],
   'note': 'Independent, time-aligned measurements give the owner, EPC contractor and network operator a common record of operating conditions.'},
  {'num': '03', 'title': 'Healthcare and Laboratories', 'img': 'IMG2',
   'p1': 'Warranty or service review may require evidence of the supply conditions present while the equipment was operating. A spot measurement may miss intermittent events.',
   'findings': ['Recorded supply conditions compared with manufacturer requirements.',
                'Evidence relevant to distinguishing supply-related events from equipment faults.',
                'Recommended next checks prioritized by technical criticality and operational impact.'],
   'statLabel': 'Technical note',
   'statText': 'IEC 60601-1-2 includes immunity testing for voltage dips and short interruptions in medical electrical equipment.',
   'statSource': 'Source: IEC'},
  {'num': '04', 'title': 'Data Centers and IT Infrastructure', 'img': 'IMG3',
   'p1': 'Generators start and transfer on a different time scale from millisecond-level disturbances. Time-stamped monitoring records can be compared with UPS and IT logs.',
   'findings': ['UPS input loading relative to rated capacity.',
                'Correlation between restarts, battery operation and recorded supply disturbances.',
                'Load profiles relevant to planned expansion.'],
   'stat': '57%', 'statLabel': 'Statistic',
   'statText': "of respondents to Uptime's 2025 annual survey said their most recent major outage cost more than USD 100,000.",
   'statSource': 'Source: Uptime Institute, Annual Outage Analysis 2026'},
  {'num': '05', 'title': 'Commercial Buildings', 'img': 'IMG4',
   'p1': 'Measurements can help distinguish upstream supply conditions from disturbances generated within the building or by tenant equipment.',
   'findings': ['Evidence relevant to the likely source of a disturbance.',
                'Electrical conditions associated with overheating or protective-device operation.',
                'Power factor, reactive power and load trends relevant to billing or capacity.'],
   'statLabel': 'Technical note',
   'statText': 'Power-quality events can originate on either side of the customer meter.',
   'statSource': 'Source: U.S. DOE / LBNL'},
  {'num': '06', 'title': 'Investment and Technical Review', 'img': 'IMG5',
   'p1': 'Diagnostic or continuous monitoring provides an independent record under actual operation. The findings can support technical due diligence, handover, warranty review or performance assessment.',
   'findings': ['Observed loading and power quality at relevant points.',
                'Recorded conditions associated with interruptions or reduced output.',
                'Limitations, risks and recommended further checks.'],
   'note': 'Reports can be prepared in Armenian, Russian or English.'},
 ],
}

# ---------------------------------------------------------------- HY
HY = {
 'LANG': 'hy', 'TITLE': 'Gridec | Էլեկտրաէներգիայի որակի մոնիթորինգ',
 'FONTFACES': FF_HY + '\n' + FF_DEP,
 'READOUT': READOUT_HY % dict(mono=MONO_HY),
 'BODYFONT': "'Arian AMU','Helvetica Neue',sans-serif",
 'HEADFONT': "'Arian AMU',sans-serif",
 'MONOFONT': MONO_HY,
 'NAVFONT': "'Arian AMU Serif',Georgia,serif",
 'HEADTT': '', 'HEADLH': '1.0', 'HEADLS': '-.012em',
 'H1SIZE': 'clamp(34px,5.6vw,86px)', 'H2SIZE': 'clamp(26px,4.1vw,58px)',
 'LANG_HREF': './index.html', 'LANG_LABEL': 'EN',
 'NAV_SERVICES': 'Ծառայություններ', 'NAV_INDUSTRIES': 'Ոլորտներ', 'NAV_COMPANY': 'Ընկերություն',
 'CTA': 'Նկարագրել խնդիրը',
 'HERO_EYEBROW': 'ԷԼԵԿՏՐԱԷՆԵՐԳԻԱՅԻ ՈՐԱԿԻ ՄՈՆԻԹՈՐԻՆԳ',
 'HERO_H1': 'Ստուգեք, թե ինչպես է աշխատում ձեր <em>էլեկտրացանցը</em>',
 'HERO_P': 'Gridec-ը էլեկտրական համակարգի աշխատանքի ընթացքում գրանցում է էլեկտրական պարամետրերն ու ցանցում առաջացող շեղումները։ Մենք վերլուծում ենք գրանցված տվյալները և ներկայացնում ենք հստակ ինժեներական եզրակացություն։',
 'HERO_CTA2': 'Ինչպես է իրականացվում մոնիթորինգը',
 'RD_CAP': 'RMS ԼԱՐՈՒՄ · 10-ՐՈՊԵԱՆՈՑ ՄԻՏՈՒՄ', 'RD_NOMINAL': 'ԱՆՎԱՆԱԿԱՆ',
 'WHY_H2': 'Իրադարձությունը կարող է ավարտվել դեռևս ստուգումը սկսելուց առաջ',
 'WHY_P': 'Լարման որոշ իրադարձություններ տևում են ընդամենը միլիվայրկյաններ կամ մի քանի ցիկլ։ Ստուգման պահին չափվող արժեքները կարող են արդեն վերադարձած լինել բնականոն մակարդակի։ Մոնիթորինգը պահպանում է իրադարձության ժամանակային նշումը և դրա պահին գրանցված պայմանները։',
 'WHY_LINK': 'Տեսնել, թե որտեղ է օգնում մոնիթորինգը',
 'APP_H2': 'Որտեղ է օգնում մոնիթորինգը',
 'APP_P': 'Էլեկտրաէներգիայի որակի խնդիրները չեն սահմանափակվում մեկ ոլորտով։ Մոնիթորինգը կիրառելի է, երբ էլեկտրական պայմաններն ազդում են սարքավորումների կամ աշխատանքային գործընթացների վրա, կամ երբ ինժեներական որոշման համար անհրաժեշտ են չափված տվյալներ։',
 'OTHER_T': 'Այլ կարևոր էլեկտրական համակարգեր',
 'OTHER_P': 'Չե՞ք գտնում ձեր ոլորտն այստեղ։ Նկարագրեք խնդիրը և դրա ազդեցությունը սարքավորման աշխատանքի վրա։',
 'SVC_EYEBROW': 'ԾԱՌԱՅՈՒԹՅՈՒՆՆԵՐ', 'SVC_H2': '7-օրյա մոնիթորինգ',
 'SVC_P1': 'Էլեկտրաէներգիայի որակի տվյալները գրանցվում են համակարգի փաստացի աշխատանքի ընթացքում և վերլուծվում՝ ուսումնասիրվող խնդրի համատեքստում։',
 'SVC_P2': 'Մոնիթորինգի տևողությունն ընտրվում է աշխատանքային պայմանների բնորոշ պատկերը ստանալու համար։ Եթե խնդիրը պարբերաբար չի դրսևորվում կամ սարքավորման աշխատանքային ցիկլն ավելի երկար է, կարող է առաջարկվել ավելի երկար ժամանակահատված։',
 'SVC_STATS': stats_html([('7', 'սովորական ախտորոշման տևողություն'),
                          ('24/7', 'անընդհատ գրանցում ամբողջ ժամանակահատվածում'),
                          ('1', 'կառուցվածքային ինժեներական հաշվետվություն')]),
 'SVC_DISPLAY': 'Չափումներ՝<br>փաստացի<br><i>բեռնվածությամբ</i>',
 'SVC_STEPS': steps_html([
    ('01', 'Սահմանում ենք նպատակը', 'Հստակեցնում ենք՝ ինչ պետք է ստուգվի, որ սարքավորումն է ներգրավված և ինչ որոշման պետք է աջակցեն արդյունքները։'),
    ('02', 'Մոնիթորինգ՝ աշխատանքային ռեժիմում', 'Չափումները կատարվում են էլեկտրական համակարգի աշխատանքի ընթացքում՝ բնորոշ աշխատանքային պայմաններում։'),
    ('03', 'Ներկայացնում ենք ինժեներական գնահատում', 'Արդյունքները գնահատվում են խնդրի համատեքստում և ներկայացվում տեխնիկական հաշվետվությամբ՝ գրանցված տվյալներով հիմնավորված եզրահանգումներով և առաջարկվող հաջորդ քայլերով։')]),
 'SVC_LINK': 'Տեսնել, թե ինչ կարող է բացահայտել մոնիթորինգը',
 'REP_H2': 'Հաշվետվություն տեխնիկական որոշումների համար',
 'REP_P': 'Հաշվետվությունում չափված փաստերը տարանջատվում են ինժեներական մեկնաբանությունից և առաջարկություններից։',
 'REP_NOTE': 'Էլեկտրաէներգիայի որակի պարամետրերը չափվում են ԳՕՍՏ ԻԷԿ 61000-4-30-2017 ստանդարտով սահմանված S դասի մեթոդներով։ Հարմոնիկ և միջհարմոնիկ բաղադրիչները գնահատվում են ԻԷԿ 61000-4-7-ի համաձայն, երբ կիրառելի է։ Մատակարարման կետում արդյունքները կարող են համեմատվել Հայաստանում գործող ԳՕՍՏ 32144-2013-ի նորմերի հետ՝ չափման նպատակից և չափման կետից կախված։',
 'REP_LIST': list_html(['Չափումների շրջանակն ու կետերը', 'Մոնիթորինգի ժամանակահատվածն ու աշխատանքային պայմանները',
                        'Գրանցված իրադարձություններն ու միտումները', 'Ինժեներական մեկնաբանություն',
                        'Առկա տվյալների սահմանափակումները', 'Առաջարկվող հաջորդ քայլերը']),
 'ASG_H2': 'Տիպային աշխատանքներ',
 'ASG_P': 'Յուրաքանչյուր աշխատանք սահմանվում է տեխնիկական հարցով և անհրաժեշտ տվյալներով։',
 'ASG_CARDS': asg_html([
    ('01', 'ԽԱՓԱՆՈՒՄՆԵՐ', 'Խափանումների ուսումնասիրություն', 'Գնահատել՝ արդյոք սարքավորումների անջատումները, ազդանշանները կամ գործընթացի ընդհատումները համընկել են գրանցված էլեկտրական իրադարձությունների հետ։'),
    ('02', 'ՀԱՆՁՆՈՒՄ', 'Գործարկման և հանձնման գնահատում', 'Գրանցել էլեկտրական համակարգի աշխատանքային պայմանները՝ ընդունման, հանձնման կամ երաշխիքային ժամկետի ավարտից առաջ կատարվող ստուգման համար։'),
    ('03', 'ԱՐԵՎԱՅԻՆ', 'Արևային կայանի միացման գնահատում', 'Գնահատել լարման պայմաններն ու ինվերտորի իրադարձությունները կայանի համապատասխան կետերում և միացման կետում։'),
    ('04', 'ՏԵԽՆԻԿԱԿԱՆ ԳՆԱՀԱՏՈՒՄ', 'Չափումներ՝ տեխնիկական համալիր գնահատման համար', 'Տրամադրել բեռնվածության, էլեկտրաէներգիայի որակի և դիտարկված աշխատանքային սահմանափակումների անկախ չափումներ՝ տեխնիկական համալիր գնահատման համար։')]),
 'MEA_H2': 'Ինչ ենք չափում',
 'MEA_CHIPS': meas_html(['Լարում և հոսանք', 'Հարմոնիկներ և միջհարմոնիկներ', 'Ֆլիկեր',
                          'Լարման անկումներ', 'Լարման անհամաչափություն', 'Հզորություն և էներգիա',
                          'Իրադարձություններ', 'Ռիսկի ցուցանիշներ'], alt=1),
 'CO_EYEBROW': 'ԸՆԿԵՐՈՒԹՅՈՒՆ',
 'CO_H2': 'Անկախ տվյալներ<br>Հստակ ինժեներական գնահատում',
 'CO_P': 'Gridec-ը ստեղծվել է էլեկտրական խնդիրները չափելի դարձնելու համար։ Մենք գրանցում ենք, թե ինչպես են էլեկտրական համակարգերն աշխատում շահագործման ընթացքում, և եզրակացությունը հիմնում ենք չափված փաստերի, ոչ թե ենթադրությունների վրա։ Gridec-ը Երևանում գործող անկախ ինժեներական ընկերություն է։ Էլեկտրաէներգիայի որակի չափումներ ենք իրականացնում ամբողջ Հայաստանում։',
 'CO_SUB': 'Չափման վայրից մինչև հաշվետվություն',
 'CO_SUBP': 'Տեղադրումը, գրանցումը և վերլուծությունն իրականացվում են մեկ պատասխանատու ինժեների ղեկավարությամբ։',
 'CO_STAGES': stages_html([
    ('01 · ՏԵՂՈՒՄ', 'Չափման համակարգի տեղադրումն ու միացումը ստուգվում են նախքան գրանցումը։'),
    ('02 · ԳՐԱՆՑՈՒՄ', 'Էլեկտրական պայմանները գրանցվում են համաձայնեցված ժամանակահատվածում։'),
    ('03 · ԳՆԱՀԱՏՈՒՄ', 'Արդյունքները մեկնաբանվում են խնդրի համատեքստում և փաստաթղթավորվում։')]),
 'CT_H2': 'Ներկայացրեք խնդիրը նախնական գնահատման համար',
 'CT_P': 'Նշեք՝ ինչ է տեղի ունեցել, որ սարքավորման վրա է դա ազդել, և երբ է խնդիրը դրսևորվել կամ սովորաբար կրկնվում։ Մենք կգնահատենք՝ կարող է արդյոք մոնիթորինգը պատասխանել հարցին և չափումների ինչ շրջանակ է անհրաժեշտ։',
 'CT_CAP': 'RMS ԼԱՐՈՒՄ · 10-ՐՈՊԵԱՆՈՑ ՄԻՏՈՒՄ', 'CT_NOM': 'ԱՆՎԱՆԱԿԱՆ', 'CT_DIP': 'ԼԱՐՄԱՆ ԱՆԿՈՒՄ · 180 ՄՎՐԿ',
 'FOOT_ADDR': 'Դավթաշեն 1, 13-25, Երևան 0058, Հայաստան',
 'IM_FINDLB': 'ԻՆՉ ՀԱՐՑԵՐԻ ԿԱՐՈՂ Է ՊԱՏԱՍԽԱՆԵԼ ՀԱՇՎԵՏՎՈՒԹՅՈՒՆԸ',
 'F_H3': 'Նկարագրեք <i>էլեկտրական խնդիրը</i>',
 'F_INTRO': 'Նշեք՝ ինչ է տեղի ունեցել, երբ է խնդիրը դրսևորվել կամ սովորաբար կրկնվում, և որ սարքավորման վրա է այն ազդել։ Մենք կգնահատենք՝ կարող է արդյոք մոնիթորինգը պատասխանել հարցին և ինչ տվյալներ են անհրաժեշտ։',
 'F_CONTACT': 'ԿՈՆՏԱԿՏԱՅԻՆ ՏՎՅԱԼՆԵՐ',
 'F_NAME': 'Անուն', 'F_NAME_PH': 'Ձեր անունը',
 'F_COMPANY': 'Ընկերություն', 'F_COMPANY_PH': 'Ընկերության անվանումը',
 'F_EMAIL': 'Էլ. փոստ', 'F_PHONE': 'Հեռախոս',
 'F_APP': 'ՈԼՈՐՏ',
 'F_WHAT': 'Ի՞ՆՉ Է ՏԵՂԻ ՈՒՆԵՑԵԼ',
 'F_MSG_PH': 'Նկարագրեք անջատումը, ազդանշանը, աշխատանքի դադարեցումը կամ կրկնվող խնդիրը։ Նշեք մոտավոր ժամանակը, ազդված սարքավորումը և առկա սխալի կոդերը կամ համակարգի գրանցած իրադարձությունները։',
 'F_ATT': 'ԿՑՎՈՂ ՖԱՅԼԵՐ', 'F_ATT_OPT': '(ըստ ցանկության)',
 'F_DROP1': 'Գցեք ֆայլերն այստեղ կամ սեղմեք ընտրելու համար',
 'F_DROP2': 'Միագիծ սխեմա, վահանակի լուսանկար, ազդանշանի էկրանի պատկեր, ինվերտորի կամ UPS-ի գրանցումների արտահանված ֆայլ, նախորդ հաշվետվություն։',
 'F_SIZE_ERR': 'Կցված ֆայլերը գերազանցում են 10 ՄԲ սահմանը։ Հեռացրեք մի քանիսը։',
 'F_HINT0': 'Առավելագույնը՝ 10 ՄԲ։',
 'F_FORM_ERR': 'Լրացրեք բոլոր դաշտերը՝ անուն, ընկերություն, վավեր էլ. փոստ, հեռախոս և կարճ նկարագրություն։',
 'F_SEND': 'Ուղարկել տվյալները',
 'F_CONTACTLINE': 'sales@powertech.am · +374 41 00 00 14 · Դավթաշեն 1, 13-25, Երևան 0058 · Երկ-Ուրբ 09:00-18:00 (UTC+4)',
 'F_OK_T': 'Շնորհակալություն։',
 'F_OK_P': 'Մենք կուսումնասիրենք տրամադրված տեղեկատվությունը և կկապվենք ձեզ հետ՝ չափումների շրջանակը հստակեցնելու համար։',
 'F_CLOSE': 'Փակել',
}
import copy
HY_DATA = copy.deepcopy(EN_DATA)
HY_DATA.update({
    # Кольцо величин в герое: номер, две строки названия, признак акцента.
    # Восьмая позиция — заключение, а не измерение, поэтому помечена.
    # Армянские термины взяты из словаря самой страницы, а не переведены заново.
    'ring': [['01', 'ԼԱՐՈՒՄ', 'ՀՈՍԱՆՔ', 0], ['02', 'ՀԱՐՄՈՆԻԿՆԵՐ', '', 0],
             ['03', 'ՖԼԻԿԵՐ', '', 0], ['04', 'ԼԱՐՄԱՆ', 'ԱՆԿՈՒՄՆԵՐ', 0],
             ['05', 'ԱՆՀԱՄԱՉԱՓՈՒԹՅՈՒՆ', '', 0], ['06', 'ՀԶՈՐՈՒԹՅՈՒՆ', 'ԷՆԵՐԳԻԱ', 0],
             ['07', 'ԴԵՊՔԵՐ', '', 0], ['08', 'ՌԻՍԿԻ', 'ԳՆԱՀԱՏՈՒՄ', 1]],
 'canvasFont': '"Arian AMU Serif",Georgia,serif',
 'rdNominal': 'ԱՆՎԱՆԱԿԱՆ', 'rdDip': 'ԼԱՐՄԱՆ ԱՆԿՈՒՄ · 180 ՄՎՐԿ',
 'incident': 'Միջադեպ',
 'seq': [['01', 'Բնականոն աշխատանք'], ['02', 'Էլեկտրական իրադարձություն'],
         ['03', 'Սարքավորման անջատում կամ ազդանշան'], ['04', 'Համակարգի աշխատանքի վերականգնում'],
         ['05', 'Գրանցումը պահպանվում է վերլուծության համար']],
 'viewDetails': 'Մանրամասներ',
 'hint1': ' ֆայլ · ', 'hintN': ' ֆայլ · ', 'hintSuf': ' / 10 ՄԲ', 'hint0': 'Առավելագույնը՝ 10 ՄԲ։',
 'appTypes': ['Արտադրություն', 'Արևային կայան', 'Բժշկական կենտրոն կամ լաբորատորիա',
              'Տվյալների կենտրոն կամ ՏՏ ենթակառուցվածք', 'Կոմերցիոն տարածք',
              'Ներդրումային և տեխնիկական գնահատում', 'Այլ'],
})
HY_CARDS = [
 {'num': '01', 'title': 'Արտադրություն', 'img': 'IMG0',
  'p1': 'Պահուստային գեներատորը նախատեսված է այլ տևողության ընդհատումների համար։ Լարման կարճատև անկումը կարող է ազդել սարքավորման վրա մինչև սնուցումը պահուստային աղբյուրին փոխանցելը, ուստի իրադարձությունը պետք է գրանցվի հենց տեղի ունենալու պահին։',
  'findings': ['Գրանցված լարման անկումների ժամանակը, տևողությունը, նվազագույն RMS լարումը և այն ֆազերը, որոնցում դրանք գրանցվել են։',
               'Շարժիչների աշխատանքի համար նշանակալի լարման անհամաչափությունն ու հոսանքային բեռնվածությունը։',
               'Արդյոք ռեակտիվ հզորությունը կամ հարմոնիկ աղավաղումը պահանջում են լրացուցիչ ինժեներական ուսումնասիրություն։'],
  'statLabel': 'ՏԵԽՆԻԿԱԿԱՆ ՆՇՈՒՄ',
  'statText': 'Լարման անկումներն ու կարճատև ընդհատումները կարող են անջատել էլեկտրոնային և էլեկտրամեխանիկական սարքերը և կանգնեցնել արտադրական գծերը։',
  'statSource': 'Աղբյուր՝ EPRI'},
 {'num': '02', 'title': 'Արևային կայաններ', 'img': 'IMG1',
  'p1': 'Լարման բարձրացումը կարող է պայմանավորված լինել կայանի արտադրած հզորության, ներքին դիմադրության և արտաքին ցանցի պայմանների փոխազդեցությամբ։ Համապատասխան կետերում կատարված չափումները օգնում են տարբերակել կայանի ներսում և արտաքին ցանցում առաջացող գործոնները։',
  'findings': ['Լարման պայմանները ինվերտորի անջատման կամ ակտիվ հզորության սահմանափակման պահին։',
               'Լարման և հարմոնիկ աղավաղման համապատասխանությունը միացման կիրառելի պահանջներին։',
               'Անկախ չափման տվյալներ՝ գործարկման ընդունման կամ EPC աշխատանքների գնահատման համար։'],
  'note': 'Ժամանակային նշումներով անկախ չափումները հնարավորություն են տալիս սեփականատիրոջը, EPC կապալառուին և ցանցի օպերատորին կայանի և միացման կետի էլեկտրական պայմանները գնահատել նույն տվյալների հիման վրա։'},
 {'num': '03', 'title': 'Բժշկական կենտրոններ և լաբորատորիաներ', 'img': 'IMG2',
  'p1': 'Երաշխիքային կամ սպասարկման գնահատման համար կարող են պահանջվել տվյալներ այն էլեկտրասնուցման պայմանների մասին, որոնցում սարքավորումն աշխատել է։ Մեկանգամյա չափումը կարող է չգրանցել պարբերաբար ի հայտ եկող իրադարձությունները։',
  'findings': ['Գրանցված էլեկտրասնուցման պայմանների համեմատությունն արտադրողի պահանջների հետ։',
               'Տվյալներ՝ էլեկտրասնուցմամբ պայմանավորված իրադարձությունները սարքավորման խափանումներից տարբերակելու համար։',
               'Հաջորդ ստուգումների առաջարկվող հերթականությունը՝ ըստ տեխնիկական կարևորության և աշխատանքի վրա ազդեցության։'],
  'statLabel': 'ՏԵԽՆԻԿԱԿԱՆ ՆՇՈՒՄ',
  'statText': 'IEC 60601-1-2-ը ներառում է բժշկական էլեկտրասարքավորումների՝ լարման անկումների և կարճատև ընդհատումների նկատմամբ խանգարումակայունության փորձարկումներ։',
  'statSource': 'Աղբյուր՝ IEC'},
 {'num': '04', 'title': 'Տվյալների կենտրոններ և ՏՏ ենթակառուցվածք', 'img': 'IMG3',
  'p1': 'Գեներատորի գործարկումն ու սնուցման փոխանցումը կատարվում են այլ ժամանակային մասշտաբով, քան միլիվայրկյան տևող խանգարումները։ Ժամանակային նշումներով մոնիթորինգի տվյալները կարելի է համադրել UPS-ի և ՏՏ համակարգերի գրանցած իրադարձությունների հետ։',
  'findings': ['UPS-ի մուտքային բեռնվածությունը՝ անվանական հզորության համեմատ։',
               'Վերագործարկումների, մարտկոցից սնուցման ռեժիմի և գրանցված էլեկտրասնուցման խանգարումների միջև կապը։',
               'Պլանավորվող ընդլայնման համար նշանակալի բեռնվածության գրաֆիկները։'],
  'stat': '57%', 'statLabel': 'ՎԻՃԱԿԱԳՐՈՒԹՅՈՒՆ',
  'statText': 'Uptime Institute-ի 2025 թ. տարեկան հարցման մասնակիցների այն բաժինը, որոնք նշել են, որ իրենց վերջին խոշոր խափանման արժեքը գերազանցել է 100 000 ԱՄՆ դոլարը։',
  'statSource': 'Աղբյուր՝ Uptime Institute, Annual Outage Analysis 2026'},
 {'num': '05', 'title': 'Կոմերցիոն տարածքներ', 'img': 'IMG4',
  'p1': 'Չափումները կարող են օգնել տարբերակել արտաքին մատակարարման ցանցի պայմանները շենքի ներքին ցանցում կամ վարձակալների սարքավորումներից առաջացող խանգարումներից։',
  'findings': ['Տվյալներ խանգարման հավանական աղբյուրը գնահատելու համար։',
               'Գերտաքացման կամ պաշտպանիչ սարքերի գործարկման հետ կապված էլեկտրական պայմանները։',
               'Հզորության գործակիցը, ռեակտիվ հզորությունը և բեռնվածության միտումները՝ վճարների կամ հասանելի հզորության գնահատման համար։'],
  'statLabel': 'ՏԵԽՆԻԿԱԿԱՆ ՆՇՈՒՄ',
  'statText': 'Էլեկտրաէներգիայի որակի իրադարձությունները կարող են առաջանալ սպառողի հաշվիչի երկու կողմում՝ մատակարարման կամ ներքին ցանցում։',
  'statSource': 'Աղբյուր՝ U.S. DOE / LBNL'},
 {'num': '06', 'title': 'Ներդրումային և տեխնիկական գնահատում', 'img': 'IMG5',
  'p1': 'Ախտորոշիչ կամ շարունակական մոնիթորինգը համակարգի փաստացի աշխատանքի անկախ գրանցում է ապահովում։ Արդյունքները կարող են օգտագործվել տեխնիկական համալիր գնահատման, հանձնման, երաշխիքային ստուգման կամ աշխատանքի արդյունավետության գնահատման համար։',
  'findings': ['Համապատասխան կետերում դիտարկված բեռնվածությունն ու էլեկտրաէներգիայի որակը։',
               'Ընդհատումների կամ արտադրողականության նվազման հետ կապված գրանցված պայմանները։',
               'Սահմանափակումները, ռիսկերը և առաջարկվող լրացուցիչ ստուգումները։'],
  'note': 'Հաշվետվությունը կարող է պատրաստվել հայերեն, ռուսերեն կամ անգլերեն։'},
]
HY_DATA['cards'] = HY_CARDS

# the seventh plate in the industries rail reuses the existing invitation copy
EN_DATA['otherT'] = EN['OTHER_T']
EN_DATA['otherP'] = EN['OTHER_P']
HY_DATA['otherT'] = HY['OTHER_T']
HY_DATA['otherP'] = HY['OTHER_P']

# ---------------------------------------------------------------- deploy variants (files by URL, not base64)
def font_face_url(fam, weight, fn):
    return ("@font-face{font-family:'%s';font-weight:%s;font-display:swap;"
            "src:url(../fonts/%s) format('woff2');}" % (fam, weight, fn))

FF_EN_D = '\n'.join([
    font_face_url('Big Shoulders Display', 700, 'big-shoulders-display-700-latin.woff2'),
    font_face_url('Archivo', 400, 'archivo-400-latin.woff2'),
    font_face_url('Archivo', 600, 'archivo-600-latin.woff2'),
    font_face_url('Martian Mono', 600, 'martian-mono-600-latin.woff2'),
])
FF_HY_D = '\n'.join([
    font_face_url('Arian AMU', '400 500', 'arian-amu-400.woff2'),
    font_face_url('Arian AMU', '600 900', 'arian-amu-700.woff2'),
    font_face_url('Arian AMU Serif', '400 500', 'arian-amu-serif-400.woff2'),
    font_face_url('Arian AMU Serif', '600 900', 'arian-amu-serif-700.woff2'),
])
IMGD_D = {'IMG%d' % i: '../uploads/img/' + f for i, f in enumerate(IMG_FILES)}

# ---------------------------------------------------------------- assemble
shell = io.open(os.path.join(HERE, 'shell.html'), encoding='utf-8').read()

def fill(tokens, data, ff, imgs):
    s = shell
    d = dict(data)
    d['imgs'] = imgs
    s = s.replace('%%DATA%%', json.dumps(d, ensure_ascii=False))
    t = dict(tokens); t['FONTFACES'] = ff
    for k, v in t.items():
        s = s.replace('%%' + k + '%%', v)
    left = re.findall(r'%%[A-Z0-9_]+%%', s)
    if left:
        raise SystemExit('UNFILLED TOKENS: %s' % sorted(set(left)))
    return s

def wrap(tokens, body, extra_head=''):
    """The description reuses the page's own opening paragraph, so nothing is invented."""
    desc = re.sub(r'<[^>]+>', '', tokens['HERO_P'])
    if len(desc) > 175:
        desc = desc[:175].rsplit(' ', 1)[0] + '\u2026'
    head = ''.join([
        '<meta charset="utf-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        '<title>', tokens['TITLE'], '</title>\n',
        '<meta name="description" content="', desc, '">\n',
        '<meta name="theme-color" content="#C8603D">\n',
        '<link rel="icon" href="../favicon.svg" type="image/svg+xml">\n',
        '<link rel="apple-touch-icon" href="../apple-touch-icon.png">\n',
        '<meta property="og:type" content="website">\n',
        '<meta property="og:title" content="', tokens['TITLE'], '">\n',
        '<meta property="og:description" content="', desc, '">\n',
        '<meta property="og:locale" content="',
        'hy_AM' if tokens['LANG'] == 'hy' else 'en_US', '">\n',
    ])
    return ('<!doctype html>\n<html lang="%s">\n<head>\n%s%s</head>\n<body>\n%s\n</body>\n</html>\n'
            % (tokens['LANG'], head, extra_head, body))

# ------------------------------------------------------------------- palettes
# REVIEW-ONLY palette passes. Each rewrites the FINISHED page, so index.html/hy.html
# keep the terracotta palette untouched and every variant is judged on the same markup.
#
# Both variants share one finding: an accent has to work on two very different grounds,
# and a single value rarely does. So each palette declares `light` (the accent for text
# and hairlines on paper) and `dark` (its twin on the graphite plates), and the extra CSS
# below wires them to --brand / --brand-ink / --brand-on so a fill always knows what
# colour of text belongs on top of it.
#
# mint: sky mint measures 1.11:1 on light paper, so it cannot carry a line, a dot or a
#   letter there at all — the light side has to use the deep mint and the mint itself
#   only appears on graphite.
# warm: the terracotta family kept, but taken down in chroma and depth. #9D5B43 reads
#   4.79:1 on its paper where the current #C8603D reads 3.70 — quieter AND more legible,
#   which is the answer to "терракота кричащий": the loudness was chroma, not hue.
PALETTES = {
    'mint': dict(
        paper='#F3F6F5', hi='#F9FBFA', lo='#EBF0EE', tint='#EEF3F1', tint2='#F6F9F8',
        ph='#DBE1DF', offwhite='#F9FCFB',
        ink='#25272C', ink2='#2A2C32', ink3='#2E3138', ink4='#313439', ink5='#292B31',
        shadow='#1C1E22',
        light='#18624C', dark='#B8F7E4', glow='#35B68F', deep='#0F2A22', err='#9E2B25',
    ),
    'warm': dict(
        paper='#F4F5F5', hi='#FAFAFA', lo='#ECEDEE', tint='#EFF0F1', tint2='#F7F8F8',
        ph='#DCDEE0', offwhite='#FBFCFC',
        ink='#25272C', ink2='#2A2C32', ink3='#2E3138', ink4='#313439', ink5='#292B31',
        shadow='#1C1E22',
        light='#9D5B43', dark='#C8856A', glow='#9D5B43', deep='#2A1610', err='#A8341F',
    ),
    # Четыре цвета заказчика: #E7F0FA бумага, #2E5E99 акцент на светлом (5,74:1),
    # #7BA4D0 акцент на плашке (6,0:1), #0D2440 плашка. Средний синий на бумаге даёт
    # 2,26:1, поэтому в светлой роли он не появляется — ровно случай sky mint.
    'blue': dict(
        paper='#E7F0FA', hi='#F1F6FD', lo='#D8E5F5', tint='#DFEAF7', tint2='#EFF5FD',
        ph='#C2D5EA', offwhite='#F5FAFE',
        ink='#0D2440', ink2='#12294A', ink3='#162E52', ink4='#183256', ink5='#102745',
        shadow='#081A31',
        light='#2E5E99', dark='#7BA4D0', glow='#4C8ACB', deep='#0A1A2E', err='#A32C26',
    ),
}

def _rgb(h):
    h = h.lstrip('#')
    return '%d,%d,%d' % tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def palette_map(p):
    """Source literals are the terracotta palette's own, so the list is the same for
    every variant — only the targets change."""
    return [
        # -- the dither bands: the accent cell follows the band's own ground
        ('#EFEDEA,#0D0E13,#C8603D', '%s,%s,%s' % (p['paper'], p['ink'], p['light'])),
        ('#14161C,#EFEDEA,#C8603D', '%s,%s,%s' % (p['ink3'], p['paper'], p['dark'])),
        # -- the section rails are drawn on both grounds, so they take the aware token
        ("tick.setAttribute('fill','#C8603D');", "tick.style.fill='var(--brand-ink)';"),
        ("pl.setAttribute('stroke','#C8603D');", "pl.style.stroke='var(--brand-ink)';"),
        # -- text sitting ON a brand fill: white is only right when the fill is dark
        ('background:var(--brand);color:#fff',
         'background:var(--brand);color:var(--brand-on)'),
        # -- the browser chrome reads as the darkest brand surface
        ('content="#C8603D"', 'content="%s"' % p['ink']),
        # -- the wave field: graphite structure, the travelling light stays chromatic
        ('--wv-line:13,14,19', '--wv-line:%s' % _rgb(p['ink'])),
        ('--wv-glow:200,96,61', '--wv-glow:%s' % _rgb(p['glow'])),
        # -- grounds
        ('#EFEDEA', p['paper']), ('rgba(239,237,234', 'rgba(%s' % _rgb(p['paper'])),
        ('#F4F3F1', p['tint']), ('rgba(244,243,241', 'rgba(%s' % _rgb(p['tint'])),
        ('#F7F5F4', p['tint2']), ('#F7F5F2', p['hi']), ('#E9E6E2', p['lo']),
        ('#DDD9D2', p['ph']),
        ('#FFFBF9', p['offwhite']), ('rgba(255,251,249', 'rgba(%s' % _rgb(p['offwhite'])),
        ('rgba(252,251,250', 'rgba(%s' % _rgb(p['offwhite'])),
        ('#0D0E13', p['ink']), ('rgba(13,14,19', 'rgba(%s' % _rgb(p['ink'])),
        ('rgba(9,10,13', 'rgba(%s' % _rgb(p['shadow'])),
        ('#111318', p['ink2']),
        ('#14161C', p['ink3']), ('rgba(20,22,28', 'rgba(%s' % _rgb(p['ink3'])),
        ('#15171E', p['ink4']),
        ('#101218', p['ink5']), ('rgba(16,18,24', 'rgba(%s' % _rgb(p['ink5'])),
        # -- accent
        ('#C8603D', p['light']), ('rgba(200,96,61', 'rgba(%s' % _rgb(p['light'])),
        ('#AC4A29', p['light']), ('#D4714E', p['dark']),
        ('#F6573D', p['dark']), ('#C5280D', p['light']), ('#c5280d', p['light'].lower()),
        ('#2C1109', p['deep']),
        # -- a failed field must not read as brand
        ('#A8341F', p['err']),
        # -- the mark is single colour under either palette; no gradient tile survives
        ("logoSet(lm?lm[1]:(ls||'1'));", "logoSet(lm?lm[1]:'1');"),
    ]

PAL_CSS = """
/* ==================== %(name)s (review palette) ====================
   --brand      accent for graphics AND fills
   --brand-ink  accent for text and hairlines
   --brand-on   what sits on top of a --brand fill
   The light grounds and the graphite plates each get the depth that works on them. */
:root{--brand:%(light)s;--brand-ink:%(light)s;--brand-on:%(paper)s;}
.plate,.plate2,.other,.chart,.ic{--brand:%(dark)s;--brand-ink:%(dark)s;--brand-on:%(ink)s;}
/* the invitation card is a brand block, and on the plates the brand is the LIGHTER of
   the two depths — so its type flips to graphite. Its edge cannot rely on the fill
   either, so it keeps a hairline. */
.ic.is-open-card{color:%(ink)s;box-shadow:0 0 0 1px rgba(%(inkrgb)s,.22);}
/* Сплошные чернила, а не .78: на фирменном фоне карточки .78 давало 4,06:1 в
   синей палитре и 3,54 в тёплой — ниже нормы для 14 пикселей. Приглушать
   абзац теперь приходится кеглем, а не выцветанием: подходящей прозрачности,
   которая проходит норму во всех трёх палитрах, попросту нет. */
.ic.is-open-card .ic-foot p{color:%(ink)s;}
.ic.is-open-card .ic-tag{background:rgba(%(inkrgb)s,.10);color:%(ink)s;}
.ic.is-open-card .ic-go{background:%(ink)s;color:%(dark)s;}
.ic.is-open-card .ic-art::after{
  background:linear-gradient(180deg,rgba(%(darkrgb)s,.10) 0%%,rgba(%(darkrgb)s,.94) 100%%);}
/* the hero's breath, in the palette's own chroma */
.hero::after{background:radial-gradient(58%% 52%% at 78%% 46%%,rgba(%(glowrgb)s,.075),transparent 70%%);}
"""

def palette_pass(name):
    p = PALETTES[name]
    css = PAL_CSS % dict(p, name=name, inkrgb=_rgb(p['ink']),
                         darkrgb=_rgb(p['dark']), glowrgb=_rgb(p['glow']))
    rules = palette_map(p)

    def run(html):
        for a, b in rules:
            html = html.replace(a, b)
        for stale in ('#C8603D', '#EFEDEA', '#0D0E13'):
            if stale in html:
                raise SystemExit('%s: terracotta literal %s survived' % (name, stale))
        return html.replace('</style>', css + '</style>', 1)
    return run

mintify = palette_pass('mint')
warmify = palette_pass('warm')
def render(tokens, data, out_body, out_full, post=None):
    s = fill(tokens, data, tokens['FONTFACES'], IMGD)
    # Переключатель языка ведёт на деплойные имена — в паре v2 это index.html и
    # hy.html. Отдельные страницы просмотра лежат рядом под своими именами, и без
    # этой подмены переключатель в них указывает в пустоту.
    s = s.replace('href="./hy.html"', 'href="./pt-hy.html"')
    s = s.replace('href="./index.html"', 'href="./pt-en.html"')
    io.open(os.path.join(HERE, out_body), 'w', encoding='utf-8').write(s)
    full = wrap(tokens, s)
    if post:
        full = post(full)
    io.open(os.path.join(HERE, out_full), 'w', encoding='utf-8').write(full)
    print(out_full, round(len(full) / 1024), 'KB')

def render_deploy(tokens, data, ff, out_path, post=None):
    s = fill(tokens, data, ff, IMGD_D)
    full = wrap(tokens, s, '<meta name="robots" content="noindex,nofollow">\n')
    if post:
        full = post(full)
    io.open(out_path, 'w', encoding='utf-8').write(full)
    print(out_path, round(len(full) / 1024), 'KB')

# Синяя палитра — базовая, а не обзорный вариант: решение принято 2026-08-04.
# Тот же пост-проход, что делает mint и warm, только применён к основным сборкам,
# поэтому английская и армянская страницы получают её одинаково.
blueify = palette_pass('blue')

render(EN, EN_DATA, 'art-en.html', 'pt-en.html', blueify)
render(HY, HY_DATA, 'art-hy.html', 'pt-hy.html', blueify)
render(EN, EN_DATA, 'art-en-mint.html', 'pt-en-mint.html', mintify)
render(EN, EN_DATA, 'art-en-warm.html', 'pt-en-warm.html', warmify)

# The deploy pair goes into the site repo's v2/. By default that is a worktree named
# `assets` sitting next to this folder; PT_V2 points the build at it wherever it lives.
V2 = os.path.join(SITE, 'v2')
os.makedirs(V2, exist_ok=True)
render_deploy(EN, EN_DATA, FF_EN_D, os.path.join(V2, 'index.html'), blueify)
render_deploy(HY, HY_DATA, FF_HY_D, os.path.join(V2, 'hy.html'), blueify)
render_deploy(EN, EN_DATA, FF_EN_D, os.path.join(V2, 'mint.html'), mintify)
render_deploy(EN, EN_DATA, FF_EN_D, os.path.join(V2, 'warm.html'), warmify)
print('done')

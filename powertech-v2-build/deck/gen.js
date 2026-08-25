// Gridec -> Janitza electronics GmbH company presentation.
// Palette values are copied from powertech-v2-build/build.py PALETTES['blue'].
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const OUT = path.join(__dirname, 'Gridec_for_Janitza.pptx');

// ---- palette -------------------------------------------------------------
const PAPER = 'F6F1E9';      // light ground
const OFFWHITE = 'FDFAF4';   // raised plane on light
const PH = 'DCD3C4';         // hairline on light
const LABEL = '8C857D';      // small mono labels on light
const INKW = '2B2722';       // text ink on light
const MUTED = '58534E';      // muted ink on light
const INK = '0D2440';        // dark plate
const ACC_L = '2E5E99';      // accent for fills / lines on light
const ACC_TXT = '20436E';    // accent for small TEXT on light
const ACC_D = '7BA4D0';      // accent on dark
const HAIR_D = '2A4670';     // hairline on dark

const HEAD = 'Arial';
const BODY = 'Arial';
const MONO = 'Consolas';

const W = 13.333, H = 7.5;
const M = 0.78;                 // page margin
const CW = W - M * 2;           // content width
const R = W - M;                // right edge

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = 'Gridec LLC';
pres.company = 'Gridec LLC';
pres.title = 'Gridec - company presentation for Janitza electronics GmbH';

const TOTAL = 8;                // numbered content slides

// ---- helpers -------------------------------------------------------------
function ground(s, dark) {
  s.background = { color: dark ? INK : PAPER };
}

// eyebrow: small accent square + letterspaced mono caps (the site's own motif)
function eyebrow(s, y, text, dark) {
  s.addShape(pres.ShapeType.rect, {
    x: M, y: y + 0.055, w: 0.062, h: 0.062,
    fill: { color: dark ? ACC_D : ACC_L }, line: { type: 'none' },
  });
  s.addText(text, {
    x: M + 0.16, y: y - 0.05, w: CW - 0.16, h: 0.26, margin: 0,
    fontFace: MONO, fontSize: 10.5, charSpacing: 1.9,
    color: dark ? ACC_D : ACC_TXT, valign: 'middle', align: 'left',
  });
}

function title(s, y, text, dark, size, h) {
  s.addText(text, {
    x: M, y: y, w: CW * 0.96, h: h || 0.62, margin: 0,
    fontFace: HEAD, fontSize: size || 32, bold: true,
    color: dark ? PAPER : INKW, lineSpacing: (size || 32) * 1.14,
    valign: 'top', align: 'left',
  });
}

function lede(s, x, y, w, text, dark, size) {
  s.addText(text, {
    x: x, y: y, w: w, h: 0.8, margin: 0,
    fontFace: BODY, fontSize: size || 12.5,
    color: dark ? 'A9B6C8' : MUTED, lineSpacing: (size || 12.5) * 1.6,
    valign: 'top', align: 'left',
  });
}

function label(s, x, y, w, text) {
  s.addText(text, {
    x: x, y: y, w: w, h: 0.24, margin: 0,
    fontFace: MONO, fontSize: 9.5, charSpacing: 1.5, color: LABEL, valign: 'middle',
  });
}

function footer(s, no, dark) {
  s.addImage({
    path: path.join(__dirname, dark ? 'wm_paper_sm.png' : 'wm_ink_sm.png'),
    x: M, y: H - 0.62, w: 0.72, h: 0.121,
    transparency: dark ? 42 : 48,
  });
  if (no) {
    s.addText(
      [
        { text: pad(no), options: { color: dark ? ACC_D : ACC_TXT } },
        { text: '  / ' + pad(TOTAL), options: { color: dark ? '6A7C96' : PH } },
      ],
      {
        x: R - 1.4, y: H - 0.68, w: 1.4, h: 0.24, margin: 0,
        fontFace: MONO, fontSize: 10, charSpacing: 1.2,
        align: 'right', valign: 'middle',
      });
  }
}

function pad(n) { return (n < 10 ? '0' : '') + n; }

function hair(s, x, y, w, dark) {
  s.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: w, h: 0.011,
    fill: { color: dark ? HAIR_D : PH }, line: { type: 'none' },
  });
}

// deterministic dither field — the site's own decoration, building left to right
let seed = 20260817;
function rnd() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function dither(s, y0, cols, rows, cell, color) {
  seed = 20260817;
  const pitch = cell * 2;
  const x0 = R - (cols - 1) * pitch - cell;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const t = Math.pow(c / (cols - 1), 1.45);
      if (rnd() > t * 0.98) continue;
      s.addShape(pres.ShapeType.rect, {
        x: x0 + c * pitch, y: y0 + r * pitch, w: cell, h: cell,
        fill: { color: color, transparency: Math.round(66 - 54 * t) },
        line: { type: 'none' },
      });
    }
  }
}

// a card: raised plane with a hairline outline
function card(s, x, y, w, h, dark) {
  s.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: w, h: h,
    fill: { color: dark ? INK : OFFWHITE },
    line: { color: dark ? HAIR_D : PH, width: 0.75 },
  });
}

// =========================================================================
// 1 — cover
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, true);
  dither(s, 3.02, 16, 9, 0.082, ACC_D);

  s.addImage({ path: path.join(__dirname, 'wm_paper.png'), x: M, y: 0.78, w: 2.55, h: 0.429 });

  s.addText('POWER QUALITY ENGINEERING', {
    x: M, y: 1.42, w: 6, h: 0.26, margin: 0,
    fontFace: MONO, fontSize: 10.5, charSpacing: 2.1, color: ACC_D, valign: 'middle',
  });

  s.addText('We make power\nproblems visible.', {
    x: M, y: 2.55, w: 8.2, h: 1.9, margin: 0,
    fontFace: HEAD, fontSize: 46, bold: true, color: PAPER, lineSpacing: 52,
    valign: 'top',
  });

  lede(s, M, 4.72, 5.5,
    'Measurement, engineering analysis and practical recommendations for electrical systems.',
    true, 13.5);

  hair(s, M, 6.28, 8.7, true);
  const cov = [
    ['COMPANY PRESENTATION', 'A9B6C8', 0, 2.5],
    ['YEREVAN, ARMENIA', '6A7C96', 2.6, 2.2],
    ['FOR JANITZA ELECTRONICS GMBH', '6A7C96', 5.0, 3.6],
  ];
  cov.forEach((c) => {
    s.addText(c[0], {
      x: M + c[2], y: 6.46, w: c[3], h: 0.26, margin: 0,
      fontFace: MONO, fontSize: 9.5, charSpacing: 1.35, color: c[1], valign: 'middle',
    });
  });
  s.addNotes('Gridec LLC company presentation, prepared for a discussion with '
    + 'Janitza electronics GmbH. Yerevan, Armenia.');
}

// =========================================================================
// 2 — who we are (people first)
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'WHO WE ARE', false);
  title(s, 1.16, 'A specialised, engineering-led\npower quality company', false, 32, 1.28);
  lede(s, M, 2.62, 7.4,
    'We are building Gridec as a specialised company rather than a broad electrical '
    + 'contractor. The focus is depth in power quality and direct technical work with '
    + 'the client.', false, 12.5);

  // people — the dominant block on this slide
  const pw = 3.72, pgap = 0.4, ptop = 3.86, ph = 2.44;
  label(s, M, 3.52, 4, 'PEOPLE BEHIND THE WORK');
  const people = [
    ['Hrant', ' [surname]', 'Director',
      'Business development, partner relations and project coordination.'],
    ['Vahe Avtandilyan', '', 'Electrical Engineer',
      'Field measurements, technical review and engineering analysis.'],
  ];
  people.forEach((p, i) => {
    const x = M + i * (pw + pgap);
    card(s, x, ptop, pw, ph, false);
    s.addText([
      { text: p[0], options: { color: INKW } },
      { text: p[1], options: { color: ACC_L } },
    ], {
      x: x + 0.3, y: ptop + 0.3, w: pw - 0.6, h: 0.4, margin: 0,
      fontFace: HEAD, fontSize: 19, bold: true, valign: 'middle',
    });
    s.addText(p[2], {
      x: x + 0.3, y: ptop + 0.78, w: pw - 0.6, h: 0.26, margin: 0,
      fontFace: MONO, fontSize: 10, charSpacing: 1.3, color: ACC_TXT, valign: 'middle',
    });
    s.addText(p[3], {
      x: x + 0.3, y: ptop + 1.16, w: pw - 0.6, h: 0.9, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: MUTED, lineSpacing: 17, valign: 'top',
    });
  });

  // company facts — deliberately quieter than the people block
  const rx = M + 2 * pw + 2 * pgap, rw = R - rx;
  label(s, rx, 3.52, rw, 'COMPANY');
  const facts = [
    ['Gridec LLC', 'Registered in Armenia.'],
    ['Yerevan', 'Working across Armenia, starting with Yerevan and the industrial '
      + 'and commercial sites around it.'],
  ];
  let fy = ptop;
  facts.forEach((f) => {
    hair(s, rx, fy, rw, false);
    s.addText(f[0], {
      x: rx, y: fy + 0.16, w: rw, h: 0.3, margin: 0,
      fontFace: HEAD, fontSize: 13.5, bold: true, color: INKW, valign: 'middle',
    });
    s.addText(f[1], {
      x: rx, y: fy + 0.52, w: rw, h: 0.9, margin: 0,
      fontFace: BODY, fontSize: 10.5, color: MUTED, lineSpacing: 15.5, valign: 'top',
    });
    fy += 1.24;
  });

  footer(s, 1, false);
  s.addNotes('Introduce the people first. Hrant\'s surname still has to be filled in before '
    + 'the deck goes out. Each card has room for one or two more factual lines about '
    + 'engineering background.');
}

// =========================================================================
// 3 — what we do
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'WHAT WE DO', false);
  title(s, 1.16, 'A focused power quality engineering practice', false, 32);
  lede(s, M, 2.16, 6.6,
    'We help clients understand what is actually happening in their electrical system '
    + 'before they make technical decisions.', false, 12.5);

  const items = [
    ['01', 'Measure', 'Temporary or continuous monitoring under representative operating conditions.'],
    ['02', 'Understand', 'Review events, trends, load behaviour and the electrical context around the measurements.'],
    ['03', 'Act', 'Translate the findings into clear engineering conclusions and practical next steps.'],
  ];
  const cw = 3.72, gap = 0.4, top = 3.28, ch = 2.06;
  items.forEach((it, i) => {
    const x = M + i * (cw + gap);
    card(s, x, top, cw, ch, false);
    s.addText(it[0], {
      x: x + 0.3, y: top + 0.28, w: 1, h: 0.24, margin: 0,
      fontFace: MONO, fontSize: 10.5, charSpacing: 1.4, color: ACC_TXT, valign: 'middle',
    });
    s.addText(it[1], {
      x: x + 0.3, y: top + 0.6, w: cw - 0.6, h: 0.34, margin: 0,
      fontFace: HEAD, fontSize: 17, bold: true, color: INKW, valign: 'middle',
    });
    s.addText(it[2], {
      x: x + 0.3, y: top + 1.04, w: cw - 0.6, h: 0.85, margin: 0,
      fontFace: BODY, fontSize: 11.5, color: MUTED, lineSpacing: 18, valign: 'top',
    });
  });

  label(s, M, 5.72, 2, 'CORE FOCUS');
  hair(s, M, 6.06, CW, false);
  const tags = ['Power quality monitoring', 'Root-cause analysis', 'Engineering recommendations'];
  tags.forEach((t, i) => {
    s.addText(t, {
      x: M + i * (cw + gap), y: 6.2, w: cw, h: 0.3, margin: 0,
      fontFace: BODY, fontSize: 12.5, bold: true, color: INKW, valign: 'middle',
    });
  });
  footer(s, 2, false);
  s.addNotes('Conclusions follow the measurements and the site context, not assumptions.');
}

// =========================================================================
// 4 — typical problems
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'TYPICAL PROBLEMS', false);
  title(s, 1.16, 'The issues we are built to investigate', false, 32);
  lede(s, M, 2.16, 7.2,
    'Our role is not only to record electrical parameters, but to connect the data to the way '
    + 'the system is designed and operated.', false, 12.5);

  const items = [
    ['Voltage events', 'Dips, swells, interruptions and unexpected equipment behaviour.'],
    ['Harmonics', 'Distortion linked to drives, converters, UPS systems and other non-linear loads.'],
    ['Unbalance', 'Phase loading and voltage or current asymmetry that affects equipment and losses.'],
    ['Reactive power', 'Power factor, compensation behaviour and unwanted interaction with the network.'],
    ['Load behaviour', 'Demand profiles, peaks and operating conditions that explain when problems appear.'],
    ['Post-change checks', 'Verification after equipment changes, commissioning or corrective measures.'],
  ];
  const cw = 3.72, gap = 0.4, top = 3.02, rh = 1.62, rgap = 0.26;
  items.forEach((it, i) => {
    const x = M + (i % 3) * (cw + gap);
    const y = top + Math.floor(i / 3) * (rh + rgap);
    card(s, x, y, cw, rh, false);
    s.addText(it[0], {
      x: x + 0.28, y: y + 0.3, w: cw - 0.56, h: 0.3, margin: 0,
      fontFace: HEAD, fontSize: 14.5, bold: true, color: INKW, valign: 'middle',
    });
    s.addText(it[1], {
      x: x + 0.28, y: y + 0.7, w: cw - 0.56, h: 0.7, margin: 0,
      fontFace: BODY, fontSize: 11, color: MUTED, lineSpacing: 16.5, valign: 'top',
    });
  });
  footer(s, 3, false);
}

// =========================================================================
// 5 — how we work
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'HOW WE WORK', false);
  title(s, 1.16, 'A simple engineering workflow', false, 32);
  lede(s, M, 2.16, 7.4,
    'The process stays compact: site context first, measurement second, conclusions only '
    + 'after the data is understood.', false, 12.5);

  const steps = [
    ['01', 'Site review', 'Understand the installation, the reported issue and the operating conditions.'],
    ['02', 'Measurement plan', 'Choose measurement points, duration and parameters around the actual problem.'],
    ['03', 'Monitoring', 'Capture normal operation and relevant events — typically over several days.'],
    ['04', 'Engineering review', 'Compare electrical behaviour with the equipment, load pattern and system configuration.'],
    ['05', 'Findings', 'A concise report with conclusions, priorities and recommended technical actions.'],
  ];
  const cw = 2.15, gap = 0.25, top = 3.3;
  hair(s, M, top, CW, false);
  steps.forEach((st, i) => {
    const x = M + i * (cw + gap);
    s.addShape(pres.ShapeType.rect, {
      x: x, y: top - 0.011, w: 0.34, h: 0.033,
      fill: { color: ACC_L }, line: { type: 'none' },
    });
    s.addText(st[0], {
      x: x, y: top + 0.24, w: cw, h: 0.26, margin: 0,
      fontFace: MONO, fontSize: 11, charSpacing: 1.4, color: ACC_TXT, valign: 'middle',
    });
    s.addText(st[1], {
      x: x, y: top + 0.58, w: cw, h: 0.56, margin: 0,
      fontFace: HEAD, fontSize: 15, bold: true, color: INKW, lineSpacing: 20, valign: 'top',
    });
    s.addText(st[2], {
      x: x, y: top + 1.18, w: cw, h: 1.3, margin: 0,
      fontFace: BODY, fontSize: 11, color: MUTED, lineSpacing: 16.5, valign: 'top',
    });
  });
  hair(s, M, 6.2, CW, false);
  s.addText('Duration and parameters follow the problem on the site, not a standard package.', {
    x: M, y: 6.38, w: CW, h: 0.3, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: MUTED, valign: 'middle',
  });
  footer(s, 4, false);
}

// =========================================================================
// 6 — market context
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'MARKET CONTEXT', false);
  title(s, 1.16, 'What is changing in Armenia', false, 32);
  lede(s, M, 2.16, 7.4,
    'Three developments make measured power quality data more relevant here than it was '
    + 'a few years ago.', false, 12.5);

  const themes = [
    ['Rapid growth of distributed solar',
      'Solar reached 17.2% of generation at the end of 2025, against 5.6% in 2022. '
      + 'More inverter-based generation is changing local network conditions.'],
    ['More power electronics in loads',
      'Drives, UPS systems, converters and other electronic loads increase the need to '
      + 'understand harmonics, events and the interaction between equipment.'],
    ['A developing specialist segment',
      'Power quality measurement and analysis is still a developing specialist service '
      + 'segment in Armenia, on the engineering side as well as the instrument side.'],
  ];
  const cw = 3.72, gap = 0.4, top = 3.28, ch = 2.3;
  themes.forEach((t, i) => {
    const x = M + i * (cw + gap);
    card(s, x, top, cw, ch, false);
    s.addText(t[0], {
      x: x + 0.3, y: top + 0.3, w: cw - 0.6, h: 0.66, margin: 0,
      fontFace: HEAD, fontSize: 15.5, bold: true, color: INKW, lineSpacing: 21, valign: 'top',
    });
    s.addText(t[1], {
      x: x + 0.3, y: top + 1.08, w: cw - 0.6, h: 1.1, margin: 0,
      fontFace: BODY, fontSize: 11, color: MUTED, lineSpacing: 16.5, valign: 'top',
    });
  });
  hair(s, M, 6.02, CW, false);
  s.addText('Solar figures from national generation statistics.', {
    x: M, y: 6.2, w: CW, h: 0.3, margin: 0,
    fontFace: BODY, fontSize: 10, color: LABEL, valign: 'middle',
  });
  footer(s, 5, false);
}

// =========================================================================
// 7 — where we start
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'WHERE WE START', false);
  title(s, 1.16, 'The segments we are set up for', false, 32);
  lede(s, M, 2.16, 7.4,
    'These are the sites where a measured answer is worth the most. They are target '
    + 'segments, not a list of completed projects.', false, 12.5);

  const segs = [
    ['Industrial facilities', 'Drives, welding and process lines under changing load.'],
    ['Solar and power electronics', 'Inverter behaviour, curtailment and voltage rise.'],
    ['Healthcare and laboratories', 'Imaging, cooling and sensitive instruments.'],
    ['IT and critical loads', 'UPS systems, server rooms and network equipment.'],
    ['Commercial buildings', 'Lifts, HVAC and mixed tenant equipment.'],
    ['Technical due diligence', 'Condition checks before a deal, a loan or a handover.'],
  ];
  const cw = 5.68, gap = 0.42, top = 3.24, rh = 1.06;
  segs.forEach((sg, i) => {
    const x = M + (i % 2) * (cw + gap);
    const y = top + Math.floor(i / 2) * rh;
    hair(s, x, y, cw, false);
    s.addText(sg[0], {
      x: x, y: y + 0.18, w: cw, h: 0.32, margin: 0,
      fontFace: HEAD, fontSize: 15, bold: true, color: INKW, valign: 'middle',
    });
    s.addText(sg[1], {
      x: x, y: y + 0.56, w: cw - 0.3, h: 0.4, margin: 0,
      fontFace: BODY, fontSize: 11, color: MUTED, lineSpacing: 16, valign: 'top',
    });
  });
  hair(s, M, top + 3 * rh, CW, false);
  footer(s, 6, false);
}

// =========================================================================
// 8 — what we bring
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'WHAT WE BRING', false);
  title(s, 1.16, 'Where we can be useful', false, 32);
  lede(s, M, 2.16, 7.4,
    'A manufacturer needs someone on the ground who can measure, explain the result and '
    + 'stay with the client afterwards.', false, 12.5);

  const rows = [
    ['Engineering before product selection',
      'We start with the site and the technical question, then identify the measurement '
      + 'and monitoring approach that fits it.'],
    ['Reports and technical communication in Armenian, Russian and English',
      'This allows us to work with local technical teams as well as international owners, '
      + 'lenders and partners.'],
    ['Technical decisions based on measured data',
      'Product selection and corrective measures should follow the measured problem, '
      + 'rather than precede it.'],
    ['One contact from first visit to follow-up',
      'Site work, commissioning checks and repeat measurements after a change, without '
      + 'handing the client between companies.'],
  ];
  const top = 3.24, rh = 0.86;
  rows.forEach((rw, i) => {
    const y = top + i * rh;
    hair(s, M, y, CW, false);
    s.addText(pad(i + 1), {
      x: M, y: y + 0.2, w: 0.5, h: 0.26, margin: 0,
      fontFace: MONO, fontSize: 10, charSpacing: 1.2, color: ACC_TXT, valign: 'middle',
    });
    s.addText(rw[0], {
      x: M + 0.56, y: y + 0.16, w: 4.62, h: 0.6, margin: 0,
      fontFace: HEAD, fontSize: 12.5, bold: true, color: INKW, lineSpacing: 17, valign: 'top',
    });
    s.addText(rw[1], {
      x: M + 5.34, y: y + 0.16, w: CW - 5.34, h: 0.6, margin: 0,
      fontFace: BODY, fontSize: 10.5, color: MUTED, lineSpacing: 15.5, valign: 'top',
    });
  });
  hair(s, M, top + rows.length * rh, CW, false);
  footer(s, 7, false);
}

// =========================================================================
// 9 — proposed cooperation
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, false);
  eyebrow(s, 0.72, 'PROPOSED COOPERATION', false);
  title(s, 1.16, 'What we would like to build with Janitza', false, 32);
  lede(s, M, 2.16, 7.4,
    'Our goal is a long-term technical relationship built around measurement quality, '
    + 'product knowledge and local engineering support.', false, 12.5);

  const steps = [
    ['01', 'Start well',
      'Training and product knowledge before we scale the offer.'],
    ['02', 'Use the right tools',
      'Mobile power quality analyzers and GridVis as the core working platform, with '
      + 'practical capability built through training and use.'],
    ['03', 'Build local capability',
      'Local measurement capability, analysis and customer support inside Armenia.'],
    ['04', 'Grow over time',
      'From single diagnostic projects toward continuous monitoring and deeper integration.'],
  ];
  const cw = 2.79, gap = 0.34, top = 3.3, ch = 2.3;
  steps.forEach((st, i) => {
    const x = M + i * (cw + gap);
    card(s, x, top, cw, ch, false);
    s.addText(st[0], {
      x: x + 0.28, y: top + 0.28, w: 0.8, h: 0.26, margin: 0,
      fontFace: MONO, fontSize: 11, charSpacing: 1.4, color: ACC_TXT, valign: 'middle',
    });
    s.addText(st[1], {
      x: x + 0.28, y: top + 0.64, w: cw - 0.56, h: 0.34, margin: 0,
      fontFace: HEAD, fontSize: 15.5, bold: true, color: INKW, valign: 'middle',
    });
    s.addText(st[2], {
      x: x + 0.28, y: top + 1.1, w: cw - 0.56, h: 1.4, margin: 0,
      fontFace: BODY, fontSize: 11, color: MUTED, lineSpacing: 16.5, valign: 'top',
    });
  });
  footer(s, 8, false);
  s.addNotes('Tone: learn the products properly, build local capability, grow the '
    + 'relationship over time.');
}

// =========================================================================
// 10 — closing
// =========================================================================
{
  const s = pres.addSlide();
  ground(s, true);
  dither(s, 4.28, 16, 8, 0.082, ACC_D);

  s.addImage({ path: path.join(__dirname, 'wm_paper.png'), x: M, y: 0.78, w: 2.55, h: 0.429 });
  s.addText('NEXT STEP', {
    x: M, y: 1.42, w: 6, h: 0.26, margin: 0,
    fontFace: MONO, fontSize: 10.5, charSpacing: 2.1, color: ACC_D, valign: 'middle',
  });

  s.addText('We would be glad to welcome the\nJanitza team in Armenia and continue\nthe discussion in person.', {
    x: M, y: 2.5, w: 8.8, h: 2.1, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true, color: PAPER, lineSpacing: 44, valign: 'top',
  });

  hair(s, M, 5.36, 7.4, true);
  const cont = [
    ['GRIDEC LLC', 'Yerevan, Armenia'],
    ['E-MAIL', 'sales@gridec.am'],
    ['WEB', 'gridec.am'],
  ];
  cont.forEach((c, i) => {
    const x = M + i * 2.6;
    s.addText(c[0], {
      x: x, y: 5.56, w: 2.4, h: 0.24, margin: 0,
      fontFace: MONO, fontSize: 9.5, charSpacing: 1.4, color: '6A7C96', valign: 'middle',
    });
    s.addText(c[1], {
      x: x, y: 5.84, w: 2.4, h: 0.3, margin: 0,
      fontFace: BODY, fontSize: 13, bold: true, color: PAPER, valign: 'middle',
    });
  });

  s.addText('Prepared for discussion with Janitza electronics GmbH.', {
    x: M, y: 6.72, w: 8.6, h: 0.3, margin: 0,
    fontFace: BODY, fontSize: 9.5, color: '6A7C96', valign: 'middle',
  });
  s.addNotes('A visit to Armenia in October was mentioned on the Janitza side.');
}

pres.writeFile({ fileName: OUT }).then(() => {
  console.log('written', OUT, fs.statSync(OUT).size, 'bytes');
});

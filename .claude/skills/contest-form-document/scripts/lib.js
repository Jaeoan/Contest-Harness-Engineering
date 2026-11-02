// Shared helpers for the report and summary documents (A4, Korean).
const fs = require('fs')
const path = require('path')
const d = require('docx')

const FONT = '맑은 고딕'
const INK = '1D1F22'
const MUTED = '6B717A'
const RULE = 'BFBAB0'
const HEAD_FILL = 'E8EEF8' // 공고 양식의 하늘색 머리 칸
const FORM_LINE = '444444'
const BLUE = '1F3FD1'
const A4 = { width: 11906, height: 16838 }
const MARGIN = 1134 // 2cm
const CONTENT = A4.width - MARGIN * 2 // 9638 dxa

const run = (text, o = {}) => new d.TextRun({ text, font: FONT, size: o.size ?? 21, bold: o.bold, color: o.color ?? INK, italics: o.italics })

/** Inline **bold** support: "보통 **굵게** 보통" */
function runs(text, o = {}) {
  return text.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((t) =>
    t.startsWith('**') ? run(t.slice(2, -2), { ...o, bold: true }) : run(t, o))
}

const p = (text, o = {}) => new d.Paragraph({
  children: runs(text, o), spacing: { after: o.after ?? 120, line: 300 }, alignment: o.align,
})
const note = (text) => p(text, { size: 17, color: MUTED, after: 160 })
// 장 제목: 공고 양식처럼 하늘색 칸 막대(한 칸 표). 앞뒤 간격은 빈 문단으로
const fline = { style: d.BorderStyle.SINGLE, size: 6, color: FORM_LINE }
const h1 = (text) => [
  new d.Paragraph({ keepNext: true, spacing: { before: 240, after: 0 }, children: [] }),
  new d.Table({
    width: { size: CONTENT, type: d.WidthType.DXA }, columnWidths: [CONTENT],
    rows: [new d.TableRow({ cantSplit: true, children: [new d.TableCell({
      width: { size: CONTENT, type: d.WidthType.DXA }, borders: { top: fline, bottom: fline, left: fline, right: fline },
      shading: { fill: HEAD_FILL, type: d.ShadingType.CLEAR, color: 'auto' }, margins: { top: 80, bottom: 80, left: 140, right: 140 },
      children: [new d.Paragraph({ keepNext: true, heading: d.HeadingLevel.HEADING_1, spacing: { before: 0, after: 0 }, children: [run(text, { size: 25, bold: true })] })],
    })] })],
  }),
  new d.Paragraph({ keepNext: true, spacing: { before: 0, after: 120 }, children: [] }),
]
const h2 = (text) => new d.Paragraph({ keepNext: true, heading: d.HeadingLevel.HEADING_2, children: [run(text, { size: 25, bold: true })], spacing: { before: 280, after: 120 } })
const h3 = (text) => new d.Paragraph({ keepNext: true, heading: d.HeadingLevel.HEADING_3, children: [run(text, { size: 22, bold: true })], spacing: { before: 200, after: 80 } })
const bullets = (items, level = 0) => items.map((t) => new d.Paragraph({
  numbering: { reference: 'bullets', level }, children: runs(t), spacing: { after: 60, line: 290 },
}))
const pageBreak = () => new d.Paragraph({ children: [new d.PageBreak()] })

const border = { style: d.BorderStyle.SINGLE, size: 4, color: RULE }
const borders = { top: border, bottom: border, left: border, right: border }

/** table(rows, widthsInPercent, {head:true}) — first row is the header */
function table(rows, pct, o = {}) {
  const widths = pct.map((x) => Math.round((CONTENT * x) / 100))
  widths[widths.length - 1] += CONTENT - widths.reduce((a, b) => a + b, 0)
  const size = o.size ?? 18
  const total = o.width ?? CONTENT
  if (o.width) { for (let i = 0; i < widths.length; i++) widths[i] = Math.round((total * pct[i]) / 100); widths[widths.length - 1] += total - widths.reduce((a, b) => a + b, 0) }
  return new d.Table({
    width: { size: total, type: d.WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, i) => new d.TableRow({
      cantSplit: true,
      tableHeader: i === 0,
      children: r.map((cell, j) => new d.TableCell({
        width: { size: widths[j], type: d.WidthType.DXA },
        borders,
        shading: i === 0 ? { fill: HEAD_FILL, type: d.ShadingType.CLEAR, color: 'auto' } : undefined,
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: String(cell).split('\n').map((line) => new d.Paragraph({
          children: runs(line, { size, bold: i === 0 }), spacing: { after: 0, line: 260 },
        })),
      })),
    })),
  })
}

/** figure(file, widthCm, caption) — keeps the image's aspect ratio */
function figure(file, widthCm, caption) {
  const buf = fs.readFileSync(file)
  const w = buf.readUInt32BE(16)
  const h = buf.readUInt32BE(20)
  const px = Math.round(widthCm * 37.8)
  return [
    new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { before: 120, after: 60 }, children: [
      new d.ImageRun({ type: 'png', data: buf, transformation: { width: px, height: Math.round((px * h) / w) },
        altText: { title: caption, description: caption, name: path.basename(file) } }),
    ] }),
    new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { after: 200 }, children: [run(caption, { size: 17, color: MUTED })] }),
  ]
}

const footer = () => new d.Footer({ children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.TextRun({ children: [d.PageNumber.CURRENT], font: FONT, size: 16, color: MUTED })] })] })

/** 여러 문서를 한 파일로(통합 제출본). parts: [{children, margin?, pageNumbers?}] — 문서마다 새 구역, 쪽 번호는 1부터 */
function docMulti(parts, title) {
  return new d.Document({
    creator: '', title,
    styles: { default: { document: { run: { font: FONT, size: 21 } } } },
    ...NUMBERING,
    sections: parts.map((p) => ({
      properties: { page: { size: A4, margin: p.margin ?? { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN }, pageNumbers: { start: 1 } } },
      footers: p.pageNumbers ? { default: footer() } : undefined,
      children: p.children.flat(),
    })),
  })
}

const NUMBERING = {
  numbering: { config: [{ reference: 'bullets', levels: [
    { level: 0, format: d.LevelFormat.BULLET, text: '○', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 240 } } } },
    { level: 1, format: d.LevelFormat.BULLET, text: '-', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 240 } } } },
  ] }, { reference: 'form', levels: [
    { level: 0, format: d.LevelFormat.BULLET, text: '❍', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 300 } } } },
    { level: 1, format: d.LevelFormat.BULLET, text: '-', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 640, hanging: 200 } } } },
  ] }] },
}

function doc(children, title) {
  return new d.Document({
    creator: '', title,
    styles: { default: { document: { run: { font: FONT, size: 21 } } } },
    numbering: { config: [{ reference: 'bullets', levels: [
      { level: 0, format: d.LevelFormat.BULLET, text: '○', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 240 } } } },
      { level: 1, format: d.LevelFormat.BULLET, text: '-', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 240 } } } },
    ] }, { reference: 'form', levels: [
      { level: 0, format: d.LevelFormat.BULLET, text: '❍', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 300 } } } },
      { level: 1, format: d.LevelFormat.BULLET, text: '-', alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 640, hanging: 200 } } } },
    ] }] },
    sections: [{
      properties: { page: { size: A4, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
      footers: { default: new d.Footer({ children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.TextRun({ children: [d.PageNumber.CURRENT], font: FONT, size: 16, color: MUTED })] })] }) },
      children: children.flat(),
    }],
  })
}

async function save(document, file) {
  fs.writeFileSync(file, await d.Packer.toBuffer(document))
  console.log('saved', file)
}

/** 수식 한 줄(가운데, 기울임) + 오른쪽 식 번호 */
function eq(text, no) {
  return new d.Paragraph({
    alignment: d.AlignmentType.CENTER, spacing: { before: 80, after: 120 },
    children: [run(text, { size: 22, italics: true }), ...(no ? [run(`    (${no})`, { size: 20 })] : [])],
  })
}

/** 본문 문단: 첫 줄 들여쓰기, 양쪽 정렬 */
function para(text, o = {}) {
  return new d.Paragraph({ children: runs(text, o), alignment: d.AlignmentType.JUSTIFIED,
    indent: { firstLine: 220 }, spacing: { after: 120, line: 320 } })
}

/** 요약 상자: 회색 바탕 한 칸 표, 각 줄 앞에 ■ */
function keybox(lines, width = CONTENT) {
  return new d.Table({
    width: { size: width, type: d.WidthType.DXA }, columnWidths: [width],
    rows: [new d.TableRow({ cantSplit: true, children: [new d.TableCell({
      width: { size: width, type: d.WidthType.DXA }, borders,
      shading: { fill: 'F4F7FC', type: d.ShadingType.CLEAR, color: 'auto' },
      margins: { top: 100, bottom: 100, left: 160, right: 160 },
      children: lines.map((l) => new d.Paragraph({ children: runs('■ ' + l, { size: 20 }), spacing: { after: 40, line: 280 } })),
    })] })],
  })
}

/** 공고 양식 머리 상자: 공모전명(「…」) + 파란 글씨 문서 종류 */
function formTitle(kind, contest) {
  const thick = { style: d.BorderStyle.SINGLE, size: 18, color: '000000' }
  return [
    new d.Table({
      width: { size: CONTENT, type: d.WidthType.DXA }, columnWidths: [CONTENT],
      rows: [new d.TableRow({ children: [new d.TableCell({
        width: { size: CONTENT, type: d.WidthType.DXA }, borders: { top: thick, bottom: thick, left: thick, right: thick },
        margins: { top: 100, bottom: 100, left: 160, right: 160 },
        children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [run(contest + ' ', { size: 25, bold: true }), run(kind, { size: 27, bold: true, color: BLUE })] })],
      })] })],
    }),
    new d.Paragraph({ spacing: { after: 160 }, children: [] }),
  ]
}

/** 양식 표 칸 안에 들어가는 본문 폭(칸 좌우 여백 140씩 제외) */
const INNER = CONTENT - 280

/** 칸 합치기가 되는 양식 표. 칸: 문자열 또는 {t, span, head, sub, align, bold, size}
 *  또는 {body: [문단·표·그림…], span} — 본문 칸은 쪽을 넘어 이어질 수 있다 */
function formTable(rows, pct, o = {}) {
  const widths = pct.map((x) => Math.round((CONTENT * x) / 100))
  widths[widths.length - 1] += CONTENT - widths.reduce((a, b) => a + b, 0)
  const size = o.size ?? 18
  const outer = { style: d.BorderStyle.SINGLE, size: 12, color: '000000' }
  return new d.Table({
    width: { size: CONTENT, type: d.WidthType.DXA }, columnWidths: widths, layout: d.TableLayoutType.FIXED,
    borders: { top: outer, bottom: outer, left: outer, right: outer, insideHorizontal: fline, insideVertical: fline },
    rows: rows.map((r, i) => {
      let col = 0
      const hasBody = r.some((raw) => raw && raw.body)
      return new d.TableRow({
        tableHeader: o.header && i === 0, cantSplit: !hasBody,
        children: r.map((raw) => {
          const c = typeof raw === 'string' ? { t: raw } : raw
          const span = c.span ?? 1
          const w = widths.slice(col, col + span).reduce((a, b) => a + b, 0)
          col += span
          const fill = c.head || c.band ? HEAD_FILL : c.sub ? 'F4F7FC' : undefined
          if (c.body) {
            const kids = c.body.flat()
            if (!(kids[kids.length - 1] instanceof d.Paragraph)) kids.push(new d.Paragraph({ spacing: { after: 0 }, children: [] }))
            // 이어지는 본문 줄(cont/more)은 사이 가로줄을 지워 한 칸처럼 보이게 한다
            const none = { style: d.BorderStyle.NONE, size: 0, color: 'FFFFFF' }
            return new d.TableCell({ width: { size: w, type: d.WidthType.DXA }, columnSpan: span > 1 ? span : undefined,
              borders: { top: c.cont ? none : fline, bottom: c.more ? none : fline, left: fline, right: fline },
              margins: { top: c.cont ? 20 : 120, bottom: c.more ? 20 : 120, left: 140, right: 140 }, children: kids })
          }
          return new d.TableCell({
            width: { size: w, type: d.WidthType.DXA }, columnSpan: span > 1 ? span : undefined, verticalAlign: d.VerticalAlign.CENTER,
            shading: fill ? { fill, type: d.ShadingType.CLEAR, color: 'auto' } : undefined,
            margins: { top: 60, bottom: 60, left: c.band ? 140 : 100, right: 100 },
            children: String(c.t).split(String.fromCharCode(10)).map((line) => new d.Paragraph({
              keepNext: c.band, alignment: c.align ?? (c.head ? d.AlignmentType.CENTER : d.AlignmentType.LEFT), spacing: { after: 0, line: 260 },
              children: runs(line, { size: c.size ?? size, bold: c.head || c.bold || c.band }),
            })),
          })
        }),
      })
    }),
  })
}

/** 요약서 칸: 테두리 상자 안에 ▢ 제목 + ❍ / - 목록. items: 문자열(❍) 또는 문자열 배열(앞 ❍의 - 세부).
 *  extra: [items 순번, ...끼워 넣을 문단] — 그 항목 바로 뒤에 그림 등을 넣는다 */
function boxChildren(heading, items, extra = []) {
  const children = [new d.Paragraph({ spacing: { after: 80 }, children: [run(`▢ ${heading}`, { size: 24, bold: true })] })]
  for (const it of items) {
    const list = Array.isArray(it) ? it.map((t) => [t, 1]) : [[it, 0]]
    for (const [t, level] of list) children.push(new d.Paragraph({ numbering: { reference: 'form', level }, spacing: { after: 40, line: 270 }, children: runs(t, { size: level ? 18 : 19 }) }))
    if (extra.length && it === items[extra[0]]) children.push(...extra.slice(1))
  }
  return children
}

/** 요약서 본문: 공고 양식처럼 ▢ 칸들을 한 장의 표(칸 사이 가로줄)로 묶는다. boxes: [[heading, items, extra?], ...] */
function formBoxes(boxes) {
  return new d.Table({
    width: { size: CONTENT, type: d.WidthType.DXA }, columnWidths: [CONTENT],
    borders: { top: fline, bottom: fline, left: fline, right: fline, insideHorizontal: fline, insideVertical: fline },
    rows: boxes.map(([h, items, extra]) => new d.TableRow({ children: [new d.TableCell({
      width: { size: CONTENT, type: d.WidthType.DXA }, margins: { top: 100, bottom: 100, left: 140, right: 140 },
      children: boxChildren(h, items, extra),
    })] })),
  })
}

function formBox(heading, items, extra = []) {
  const children = boxChildren(heading, items, extra)
  return [
    new d.Table({
      width: { size: CONTENT, type: d.WidthType.DXA }, columnWidths: [CONTENT],
      rows: [new d.TableRow({ children: [new d.TableCell({
        width: { size: CONTENT, type: d.WidthType.DXA }, borders: { top: fline, bottom: fline, left: fline, right: fline },
        margins: { top: 100, bottom: 100, left: 140, right: 140 }, children,
      })] })],
    }),
    new d.Paragraph({ spacing: { after: 0 }, children: [] }),
  ]
}


/** 수상작 문체용: □ 주장형 소제목 */
const sq = (text) => new d.Paragraph({ keepNext: true, heading: d.HeadingLevel.HEADING_2, spacing: { before: 300, after: 120 }, children: [run(`□ ${text}`, { size: 24, bold: true })] })
/** 본문 문단(~습니다 체, 들여쓰기 없음, 양쪽 정렬) */
const P = (text, o = {}) => new d.Paragraph({ alignment: d.AlignmentType.JUSTIFIED, spacing: { after: o.after ?? 110, line: 310 }, keepNext: o.keepNext, children: runs(text, { size: o.size ?? 21 }) })
/** 출처 줄: 매체 "제목" URL */
const src = (list) => list.map(([who, title, url]) => new d.Paragraph({ spacing: { after: 20, line: 240 }, children: [
  run(`${who} `, { size: 16, color: MUTED }), run(`"${title}" `, { size: 16, color: MUTED }), run(url, { size: 16, color: '1F5FBF' }),
] }))

/** 아주 작은 출처 줄: refs(인용 키 배열) → "출처: 매체(날짜) URL · …" */
function cite(refs, keys) {
  const list = keys.map((k) => { const r = typeof k === 'object' ? k : refs.find((x) => x.cite === k); if (!r) throw new Error('cite 없음: ' + k); return r })
  return new d.Paragraph({ spacing: { before: 20, after: 100, line: 220 }, children: [
    run('출처: ', { size: 13, color: MUTED }),
    ...list.flatMap((r, i) => [
      ...(i ? [run(' · ', { size: 13, color: MUTED })] : []),
      // 법령처럼 제목에 인용 키가 들어 있으면 키를 반복하지 않는다. 제목 뒤 괄호·줄표 설명은 뺀다
      run(r.title.includes(r.cite) ? `${r.title.replace(/\s*—.*$/, '')} ` : `${r.cite} 「${r.title.replace(/\s*\(.*\)$/, '')}」 `, { size: 13, color: MUTED }),
      run(r.url.replace(/^https?:\/\//, ''), { size: 13, color: '1F5FBF' }),
    ]),
  ] })
}

module.exports = { INNER, cite, docMulti, sq, P, src, formTitle, formTable, formBox, formBoxes, eq, para, keybox, p, note, h1, h2, h3, bullets, table, figure, pageBreak, doc, save, run, runs, d }

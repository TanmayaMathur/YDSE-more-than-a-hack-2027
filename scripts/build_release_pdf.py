"""Build a separate final technical PDF, never touching prior candidate documents."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Preformatted,PageBreak,Table,TableStyle
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]


def clean(s):
    for a,b in [('—','-'),('–','-'),('‑','-'),('−','-'),('→','->'),('↔','<->'),('×','x'),('’',"'"),('\u00a0',' ')]:s=s.replace(a,b)
    return s


def inline(s):
    s=html.escape(clean(s))
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    return re.sub(r'`([^`]+)`',r'<font name="Courier" size="8">\1</font>',s)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'private/release_audit/submission_bundle/YDSE.pdf')
    args=ap.parse_args();target=args.out.resolve()
    if target.exists():raise FileExistsError('Use a new PDF path; never replace an existing release document')
    target.parent.mkdir(parents=True,exist_ok=True)
    font='Helvetica';bold='Helvetica-Bold';fonts=Path('C:/Windows/Fonts')
    if (fonts/'arial.ttf').exists():
        pdfmetrics.registerFont(TTFont('ReleaseArial',str(fonts/'arial.ttf')))
        pdfmetrics.registerFont(TTFont('ReleaseArialBold',str(fonts/'arialbd.ttf')))
        pdfmetrics.registerFontFamily('ReleaseArial',normal='ReleaseArial',bold='ReleaseArialBold')
        font='ReleaseArial';bold='ReleaseArialBold'
    ink=colors.HexColor('#183044');muted=colors.HexColor('#526679')
    body=ParagraphStyle('ReleaseBody',fontName=font,fontSize=9.4,leading=12.3,spaceAfter=6,textColor=ink)
    title=ParagraphStyle('ReleaseTitle',parent=body,fontName=bold,fontSize=21,leading=25,spaceAfter=11)
    head=ParagraphStyle('ReleaseHeading',parent=body,fontName=bold,fontSize=12,leading=16,spaceBefore=7,spaceAfter=7,keepWithNext=True)
    code=ParagraphStyle('ReleaseCode',fontName='Courier',fontSize=7.6,leading=10,spaceBefore=3,spaceAfter=8,
        backColor=colors.HexColor('#f0f4f7'),borderPadding=5)
    story=[];paragraph=[];code_lines=[];tab=[];inside=False
    def flush():
        if paragraph:story.append(Paragraph(inline(' '.join(paragraph)),body));paragraph.clear()
    def flush_table():
        if not tab:return
        rows=[r for r in tab if not all(re.fullmatch(r':?-+:?',v.strip()) for v in r)]
        values=[[Paragraph(inline(v),body) for v in row] for row in rows]
        widths=[92*mm,38*mm,38*mm] if len(rows[0])==3 else None
        table=Table(values,colWidths=widths,hAlign='LEFT',repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf3')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#b5c6d2')),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        story.append(table);tab.clear()
    for line in (ROOT/'docs/release_technical_report.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('```'):
            flush();flush_table()
            if inside:story.append(Preformatted('\n'.join(clean(x) for x in code_lines),code));code_lines.clear()
            inside=not inside;continue
        if inside:code_lines.append(line);continue
        if line.startswith('|'):
            flush();tab.append([x.strip() for x in line.strip('|').split('|')]);continue
        flush_table()
        if line=='<!-- pagebreak -->':flush();story.append(PageBreak())
        elif line.startswith('# '):flush();story.append(Paragraph(inline(line[2:]),title))
        elif line.startswith('## '):flush();story.append(Paragraph(inline(line[3:]),head))
        elif not line.strip():flush()
        else:paragraph.append(line.strip())
    flush();flush_table()
    def page(canvas,doc):
        w,h=doc.pagesize;canvas.saveState();canvas.setStrokeColor(colors.HexColor('#cad6df'))
        canvas.setLineWidth(.5);canvas.line(20*mm,h-13*mm,w-20*mm,h-13*mm)
        canvas.setFont(font,8);canvas.setFillColor(muted)
        canvas.drawString(20*mm,12*mm,'YDSE / Frozen V3 / Final technical document')
        canvas.drawRightString(w-20*mm,12*mm,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(str(target),pagesize=(210*mm,297*mm),leftMargin=20*mm,rightMargin=20*mm,
        topMargin=19*mm,bottomMargin=20*mm,title='YDSE - Final Technical Document - Frozen V3',author='YDSE').build(story,onFirstPage=page,onLaterPages=page)
    reader=PdfReader(target);text='\n'.join(p.extract_text() for p in reader.pages)
    for required in ['82,329','0.4799','0.4235','199,319','reproduction','11,449']:
        assert required in text,required
    assert len(reader.pages)==3,f'Inspect unexpected pagination: {len(reader.pages)} pages'
    result=dict(path=str(target),pages=len(reader.pages),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        text_check='PASS',source='docs/release_technical_report.md',visual_review='Required before delivery')
    (ROOT/'private/release_audit/pdf_build.json').write_text(json.dumps(result,indent=2),newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

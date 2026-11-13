"""Optional PDF from the public technical report (reportlab and pypdf required)."""
from pathlib import Path
import html
import importlib.metadata
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]

def clean(text):
    for old,new in [('—','-'),('–','-'),('‑','-'),('×','x'),('\u00a0',' '),('’',"'"),('“','"'),('”','"')]:
        text=text.replace(old,new)
    return text

def inline(text):
    text=html.escape(clean(text))
    text=re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<link color="#1a5b8c" href="\2">\1</link>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    return re.sub(r'`([^`]+)`',r'<font name="Courier" size="8.8">\1</font>',text)

def main():
    font='Helvetica';bold='Helvetica-Bold'
    base=Path('C:/Windows/Fonts')
    if (base/'arial.ttf').exists():
        pdfmetrics.registerFont(TTFont('ReportArial',str(base/'arial.ttf')))
        pdfmetrics.registerFont(TTFont('ReportArialBold',str(base/'arialbd.ttf')))
        pdfmetrics.registerFontFamily('ReportArial',normal='ReportArial',bold='ReportArialBold')
        font='ReportArial';bold='ReportArialBold'
    body=ParagraphStyle('Body',fontName=font,fontSize=10,leading=14,spaceAfter=7,textColor=colors.HexColor('#243244'))
    h1=ParagraphStyle('Title',fontName=bold,fontSize=23,leading=28,textColor=colors.HexColor('#102a43'),spaceAfter=10)
    h2=ParagraphStyle('Heading',fontName=bold,fontSize=12,leading=16,textColor=colors.HexColor('#102a43'),spaceBefore=12,spaceAfter=6,keepWithNext=True)
    meta=ParagraphStyle('Meta',fontName=font,fontSize=9,leading=13,textColor=colors.HexColor('#50667a'),spaceAfter=15)
    code=ParagraphStyle('Code',fontName='Courier',fontSize=8.1,leading=11,backColor=colors.HexColor('#f2f5f8'),borderPadding=8,spaceBefore=6,spaceAfter=10)
    target=ROOT/'submission/YDSE.pdf'
    story=[Paragraph('YDSE',h1),Paragraph('Ball possession from automatic tracking',ParagraphStyle('Subtitle',parent=h2,fontSize=15,spaceBefore=0)),
           Paragraph('More Than a Hack 2027  |  Phase 1 technical report  |  14 November 2026',meta)]
    lines=(ROOT/'docs/technical_report.md').read_text(encoding='utf-8').splitlines()
    paragraph=[];code_lines=[];inside=False
    def flush():
        if paragraph:
            story.append(Paragraph(inline(' '.join(paragraph)),body));paragraph.clear()
    for line in lines:
        if line.startswith('# '):
            continue
        if line.startswith('```'):
            flush()
            if inside:
                story.append(Preformatted('\n'.join(clean(s) for s in code_lines),code));code_lines.clear()
            inside=not inside
            continue
        if inside:
            code_lines.append(line);continue
        if line.startswith('## '):
            flush();story.append(Paragraph(inline(line[3:]),h2))
        elif not line.strip():
            flush()
        else:
            paragraph.append(line.strip())
    flush()
    def page(canvas,doc):
        width,height=doc.pagesize
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d6e0e8'));canvas.setLineWidth(.5)
        canvas.line(20*mm,height-14*mm,width-20*mm,height-14*mm)
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#50667a'))
        canvas.drawString(20*mm,12*mm,'YDSE  /  Technical report')
        canvas.drawRightString(width-20*mm,12*mm,str(doc.page))
        canvas.restoreState()
    doc=SimpleDocTemplate(str(target),pagesize=(210*mm,297*mm),leftMargin=20*mm,rightMargin=20*mm,
                          topMargin=21*mm,bottomMargin=22*mm,title='YDSE - Ball Possession Technical Report',author='YDSE')
    doc.build(story,onFirstPage=page,onLaterPages=page)
    reader=PdfReader(target)
    text='\n'.join(p.extract_text() for p in reader.pages)
    if 'Reproduction' not in text or '0.8001' not in text or len(text)<6000:
        raise RuntimeError('PDF text verification failed')
    print(f'Created {target.name}: {len(reader.pages)} pages; text checks passed.')
    print('PDF dependency versions: '+', '.join(f'{p}=={importlib.metadata.version(p)}' for p in ['reportlab','pypdf']))

if __name__=='__main__':
    main()

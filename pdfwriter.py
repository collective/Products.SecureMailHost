"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.28 2004/01/17 13:09:00 ajung Exp $
"""

import os, sys, cStringIO, tempfile
from types import UnicodeType
from textwrap import fill
from zLOG import WARNING, LOG
   
try:
    from PIL import Image as PIL_Image
    have_pil = 1
except ImportError: 
    LOG('plonecollectorng', WARNING, 'Python Imaging Library not available. Pdfwriter will not be able to include images in issue PDFs') 
    have_pil = 0

from DateTime import DateTime
from DocumentTemplate.html_quote import html_quote

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab import rl_config 
from reportlab.lib.units import inch                              
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

styles = getSampleStyleSheet()

MAX_IMAGE_SIZE = 5*inch
PAGE_HEIGHT = rl_config.defaultPageSize[1]


# Settup custom fonts for UTF8 handling
rl_config.warnOnMissingFontGlyphs = 0
rl_config.TTFSearchPath= list(rl_config.TTFSearchPath) + [ os.path.join(os.path.dirname(__file__), 'ttffonts') ]
pdfmetrics.registerFont(TTFont('NFont', 'VeraSe.ttf'))
pdfmetrics.registerFont(TTFont('NFont-Bold', 'VeraSeBd.ttf'))

NORMAL_FONT = 'NFont'
BOLD_FONT = 'NFont-Bold'

def utf8(text):
    """ Unicode -> UTF8 """
    assert isinstance(text, UnicodeType)
    return text.encode('utf-8')

def dowrap(text):
    return fill(text, 100)

def break_longlines(text):

    l = []
    for line in text.split('\n'):
        if len(line) > 100:
            l.append(dowrap(line))
        else:
            l.append(line)
    return '\n'.join(l)

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(50,45,50,PAGE_HEIGHT-45)
    canvas.line(50,PAGE_HEIGHT-70, 555, PAGE_HEIGHT-70)
    canvas.setFont(NORMAL_FONT,15)
    canvas.drawString(inch, PAGE_HEIGHT-62, utf8(doc.collector_title))
    canvas.setFont(NORMAL_FONT,11)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.drawString(450, 0.75 * inch, doc.collector.toLocalizedTime(DateTime(), long_format=1))
    canvas.restoreState()

myFirstPage = myLaterPages

Elements = []

##########################################################################
# Formatter methods
##########################################################################

HeaderStyle = styles["Heading3"] 
HeaderStyle.fontName = BOLD_FONT
HeaderStyle.spaceBefore = 3
HeaderStyle.spaceAfter = 1

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
    assert isinstance(txt, UnicodeType)
    p = XPreformatted(utf8(txt), style)
    Elements.append(p)


ParaStyle = styles["Normal"]
ParaStyle.fontName = NORMAL_FONT
ParaStyle.leftIndent = 18

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)


PreStyle = styles["Code"]
PreStyle.fontName = NORMAL_FONT

def pre(txt):
    assert isinstance(txt, UnicodeType)
    p = Preformatted(utf8(txt), PreStyle)
    Elements.append(p)


DefStyle = styles["Definition"]
DefStyle.leftIndent = 18
DefStyle.fontName = NORMAL_FONT
DefStyle.spaceBefore = 3
DefStyle.spaceAfter = 1

def definition(txt):
    assert isinstance(txt, UnicodeType)
    p = XPreformatted(utf8(txt), DefStyle)
    Elements.append(p)


##########################################################################
# PDF Writer
##########################################################################

def pdfwriter(collector, ids):

    def toUnicode(text):
        if not isinstance(text, UnicodeType):
            return unicode(text, collector.getSiteEncoding())
        return text

    translate = collector.translate

    tempfiles = []

    for issue_id in ids:
        issue = getattr(collector, str(issue_id))
        header(translate('issue_number', 'Issue #$id', id='%s: %s' % (issue.getId(), issue.title), as_unicode=1))

        header(translate('label_description', 'Description', as_unicode=1))
        definition(html_quote(issue.description))

        if issue.solution:
            header(translate('label_solution', 'Solution', as_unicode=1))
            definition(html_quote(issue.solution))

        for name in issue.atse_getSchemataNames():
            if name in ('default', 'metadata'): continue
            
            l =[]

            for field in issue.atse_getSchemata(name).fields():
                if field.getName() in ('description', 'title'): continue

                value = issue.getParameter(field.getName())

                if hasattr(field, 'vocabulary'):
                    vocab = field.Vocabulary(issue)
                    v = issue.displayValue(vocab, value)
                else:
                    v = value

                if v:
                    l.append('<b>%s</b>: %s ' % (translate(field.widget.label_msgid, field.widget.Label(issue), as_unicode=1), v))

            s = (', '.join(l)).strip()
            if s:
                header(translate(name, name.capitalize(), as_unicode=1))
                definition(dowrap(s))

        for img in issue.objectValues('Portal Image'):

            if have_pil:
                Elements.append(Spacer(100, 0.2*inch))
                fname = tempfile.mktemp() + img.getId()
                tempfiles.append(fname)
                open(fname, 'w').write(str(img.data))
                image = PIL_Image.open(fname)
                width, height= image.size
                ratio = width*1.0 / height
                
                if ratio >  1.0:
                    width = MAX_IMAGE_SIZE
                    height = width / ratio
                else:
                    height = MAX_IMAGE_SIZE
                    width = height * ratio

                istr = translate('image', 'Image', as_unicode=1)
                desc = '%s: %s' % (istr, img.getId())

                Elements.append(KeepTogether([XPreformatted(desc, HeaderStyle),
                                              Spacer(100, 0.1*inch),
                                              Image(fname, width, height),
                                              Preformatted(img.title, DefStyle)
                                             ]))

            else:
                p(u'%s: %s' % (translate('image', 'Image', as_unicode=1), img.getId()))

            Elements.append(Spacer(100, 0.2*inch))

        header(translate('transcript', 'Transcript', as_unicode=1))

        n = 1

        for group in issue.getTranscript().getEventsGrouped(reverse=0):
            datestr = issue.toLocalizedTime(DateTime(group[0].created), long_format=1)
            uid = group[0].user
            header(u'#%d %s %s (%s)' % (n, translate(issue.lastAction(), issue.lastAction().capitalize(), as_unicode=1), datestr, uid)) 

            l = []
            comment = None

            for ev in group:
                if ev.type == 'comment':
                    comment = html_quote(ev.comment)
                elif ev.type == 'change':
                    l.append(dowrap('<b>%s:</b> %s: "%s" -> "%s"' % (translate('changed', 'Changed', as_unicode=1), ev.field, ev.old, ev.new)))
                elif ev.type == 'incrementalchange':
                    l.append(dowrap('<b>%s:</b> %s: %s: %s , %s: %s' % (translate('changed', 'Changed', as_unicode=1), ev.field, translate('added', 'added', as_unicode=1), ev.added, translate('removed', 'removed', as_unicode=1), ev.removed)))
                elif ev.type == 'reference':
                    l.append(dowrap('<b>%s:</b> %s: %s/%s (%s)' % (translate('reference', 'Reference', as_unicode=1), ev.tracker, ev.ticketnum, ev.comment)))
                elif ev.type == 'upload':
                    s = '<b>%s:</b> %s/%s ' % (translate('upload', 'Upload', as_unicode=1), issue.absolute_url(), ev.fileid)
                    if ev.comment:
                        s+= ' (%s)' % ev.comment
                    l.append(dowrap(toUnicode(s)))


            definition('\n'.join(l))
            if comment: 
                definition('<b>%s</b>' % translate('comment', 'Comment', as_unicode=1))
                pre(break_longlines(comment))
            n+=1

        # references
        fw_refs = issue.getForwardReferences()
        if fw_refs:
            header(translate('references', 'References', as_unicode=1))
            definition('\n'.join(['%s: %s' % (ref.getTargetObject().absolute_url(), toUnicode(ref.comment)) for ref in fw_refs ]))

        Elements.append(PageBreak())

    IO = cStringIO.StringIO()
    doc = SimpleDocTemplate(IO)
    doc.collector = collector
    doc.collector_title = translate('collector_id', 'Collector: $id', id=collector.title, as_unicode=1)
    doc.build(Elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    for f in tempfiles:
        if os.path.exists(f):
            os.unlink(f)

    return IO.getvalue()

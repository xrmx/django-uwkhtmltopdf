from django.conf import settings
from django.template.context import Context
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils.encoding import smart_str
import subprocess
import tempfile
import StringIO
import os

try:
    WKHTMLTOPDF = settings.WKHTMLTOPDF_CMD
except AttributeError:
    WKHTMLTOPDF = '/usr/bin/wkhtmltopdf'

def render_to_tmp_file(template_name, context):
    tmpl = get_template(template_name)
    html = smart_str(tmpl.render(Context(context)))
    # wkhtmltopdf segfaults without .html suffix
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    tmp.write(html)
    name = tmp.name
    tmp.close()
    return name

def generate_pdf(template_name, file_object=None, context=None, options=None):
    """
    Uses wkhtmltopdf to render a PDF to the passed file_object, from the
    given template name. Optionally takes a template name for an header and for a footer
    to be repeated on each pdf page.

    This returns the passed-in file object, filled with the actual PDF data.
    In case the passed in file object is none, it will return a StringIO instance.
    """
    if not file_object:
        file_object = StringIO.StringIO()
    if not context:
        context = {}
    tmpl = get_template(template_name)
    html = smart_str(tmpl.render(Context(context)))

    if options is None:
        options = {}

    opts = []
    if options:
        if 'header' in options:
            header_template = render_to_tmp_file(options['header'], context)
            opts.extend(['--header-html', header_template])

        if 'footer' in options:
            footer_template = render_to_tmp_file(options['footer'], context)
            opts.extend(['--footer-html', footer_template])

        if 'margin-top' in options:
            opts.extend(['--margin-top', options['margin-top']])

        if 'margin-bottom' in options:
            opts.extend(['--margin-bottom', options['margin-bottom']])

        if 'margin-left' in options:
            opts.extend(['--margin-left', options['margin-left']])

        if 'margin-right' in options:
            opts.extend(['--margin-right', options['margin-right']])

        if 'header-spacing' in options:
            opts.extend(['--header-spacing', options['header-spacing']])

        if 'footer-spacing' in options:
            opts.extend(['--footer-spacing', options['footer-spacing']])

    cmd = [WKHTMLTOPDF] + opts + ['-', '-']
    pdf_as_string = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=html)[0]

    if 'header' in options:
        os.remove(header_template)
    if 'footer' in options:
        os.remove(footer_template)

    file_object.write(pdf_as_string)
    return file_object

def render_to_pdf_response(template_name, context=None, pdfname=None):
    file_object = HttpResponse(content_type='application/pdf')
    if not pdfname:
        pdfname = '%s.pdf' % os.path.splitext(os.path.basename(template_name))[0]
    file_object['Content-Disposition'] = 'attachment; filename=%s' % pdfname
    return generate_pdf(template_name, file_object, context)

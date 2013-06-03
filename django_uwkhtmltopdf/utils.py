from django.conf import settings
from django.template.context import Context
from django.template.loader import get_template
from django.http import HttpResponse
import subprocess
import tempfile
import StringIO
import os

def render_to_tmp_file(template_name, context):
    tmpl = get_template(template_name)
    html = tmpl.render(Context(context))
    # wkhtmltopdf segfaults without .html suffix
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    tmp.write(html)
    name = tmp.name
    tmp.close()
    return name

def generate_pdf(template_name, file_object=None, context=None, header=None, footer=None):
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
    html = tmpl.render(Context(context))

    opts = []
    if header:
        header_template = render_to_tmp_file(header, context)
        opts.extend(['--header-html', header_template])
    if footer:
        footer_template = render_to_tmp_file(footer, context)
        opts.extend(['--footer-html', footer_template])

    try:
        WKHTMLTOPDF = settings.WKHTMLTOPDF_CMD
    except AttributeError:
        WKHTMLTOPDF = '/usr/bin/wkhtmltopdf'

    cmd = [WKHTMLTOPDF] + opts + ['-', '-']
    pdf_as_string = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=html)[0]

    if header:
        os.remove(header_template)
    if footer:
        os.remove(footer_template)

    file_object.write(pdf_as_string)
    return file_object

def render_to_pdf_response(template_name, context=None, pdfname=None):
    file_object = HttpResponse(content_type='application/pdf')
    if not pdfname:
        pdfname = '%s.pdf' % os.path.splitext(os.path.basename(template_name))[0]
    file_object['Content-Disposition'] = 'attachment; filename=%s' % pdfname
    return generate_pdf(template_name, file_object, context)

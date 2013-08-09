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
    given template name. Optionally take an options dictionary which supports
    only header / footer templates to be repeated on each pdf page, page margins
    and header / footer spacing.

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
    files_to_remove = []
    for opt in options:
        if opt in ('header-html', 'footer-html'):
            if opt == 'header-html':
                header_template = render_to_tmp_file(options[opt], context)
                opts.extend(['--' + opt, header_template])
                files_to_remove.append(header_template)
            elif opt == 'footer-html':
                footer_template = render_to_tmp_file(options[opt], context)
                opts.extend(['--' + opt, footer_template])
                files_to_remove.append(footer_template)

        if opt in ('margin-top', 'margin-bottom', 'margin-left', 'margin-right'):
            opts.extend(['--' + opt , options[opt]])

        if opt in ('header-spacing', 'footer-spacing'):
            opts.extend(['--' + opt, options[opt]])

    cmd = [WKHTMLTOPDF] + opts + ['-', '-']
    pdf_as_string = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=html)[0]

    for f in files_to_remove:
        os.remove(f)

    file_object.write(pdf_as_string)
    return file_object

def render_to_pdf_response(template_name, context=None, pdfname=None):
    file_object = HttpResponse(content_type='application/pdf')
    if not pdfname:
        pdfname = '%s.pdf' % os.path.splitext(os.path.basename(template_name))[0]
    file_object['Content-Disposition'] = 'attachment; filename=%s' % pdfname
    return generate_pdf(template_name, file_object, context)

from django.conf import settings
from django.template.context import Context
from django.template.loader import get_template
from django.http import HttpResponse
import subprocess
import StringIO
import os

def generate_pdf(template_name, file_object=None, context=None):
    """
    Uses wkhtmltopdf to render a PDF to the passed file_object, from the
    given template name.

    This returns the passed-in file object, filled with the actual PDF data.
    In case the passed in file object is none, it will return a StringIO instance.
    """
    if not file_object:
        file_object = StringIO.StringIO()
    if not context:
        context = {}
    tmpl = get_template(template_name)
    html = tmpl.render(Context(context))
    try:
        WKHTMLTOPDF = settings.WKHTMLTOPDF_CMD
    except AttributeError:
        WKHTMLTOPDF = '/usr/bin/wkhtmltopdf'
    pdf_as_string = subprocess.Popen([WKHTMLTOPDF, '-n', '-', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(input=html)[0]
    file_object.write(pdf_as_string)
    return file_object

def render_to_pdf_response(template_name, context=None, pdfname=None):
    file_object = HttpResponse(content_type='application/pdf')
    if not pdfname:
        pdfname = '%s.pdf' % os.path.splitext(os.path.basename(template_name))[0]
    file_object['Content-Disposition'] = 'attachment; filename=%s' % pdfname
    return generate_pdf(template_name, file_object, context)

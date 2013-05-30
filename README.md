django-uwkhtmltopdf
===================

A simple Django app to generate pdfs from templates using wkhtmltopdf.

The code is basically a fork of django-xhtml2pdf that uses wkhtmltopdf to avoid xhtml2pdf shortcomings.

Please note that the app is thought to be simple not feature rich.

Usage
-----

In settings.py:

    WKHTMLTOPDF_CMD = '/path/to/wkhtmltopdf'

In views.py:

    from django_uwkhtmltopdf.utils import generate_pdf

    def myview(response):
        resp = HttpResponse(content_type='application/pdf')
        result = generate_pdf('my_template.html', file_object=resp)
        return result

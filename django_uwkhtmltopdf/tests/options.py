from django.test import TestCase
from django.test.utils import override_settings
from django_uwkhtmltopdf.utils import parse_options

import os

@override_settings(
    TEMPLATE_DIRS=(
        os.path.join(os.path.dirname(__file__), 'templates'),
    ),
)
class TestParseOptions(TestCase):
    def test_wrong_options(self):
        options = {'no_images': ''}
        self.assertEqual(parse_options(options, {}), ([], []))

    def test_no_parameter(self):
        options = {'no-images': ''}
        self.assertEqual(parse_options(options, {}), (['--no-images'], []))

    def test_one_parameter(self):
        options = {'minimum-font-size': 10}
        self.assertEqual(parse_options(options, {}), (['--minimum-font-size', 10], []))

    def test_two_parameters(self):
        options = {'cookie': ('name', 12)}
        self.assertEqual(parse_options(options, {}), (['--cookie', 'name', 12], []))

    def test_template_needed(self):
        files_to_remove = []
        context = {}
        options = {'header-html': 'header.html'}
        parsed_opts, files_to_remove = parse_options(options, context)
        self.assertEqual(len(files_to_remove), 1)
        self.assertEqual(parsed_opts[0], "--header-html")

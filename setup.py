from setuptools import setup, find_packages
import os
import django_uwkhtmltopdf

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="Riccardo Magliocchetti",
    author_email="riccardo.magliocchetti@gmail.com",
    name='django-uwkhtmltopdf',
    version=django_uwkhtmltopdf.__version__,
    description='A Django app to generate pdfs from templates using wkhtmltopdf',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url="https://github.com/xrmx/django-uwkhtmltopdf",
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.2',
    ],
    packages=find_packages(exclude=["example", "example.*"]),
    include_package_data=True,
    zip_safe = False,
)

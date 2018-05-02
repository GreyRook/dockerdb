#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'docker',
]

extras_require = {
    'mongo': ['pymongo'],
}

test_requirements = []

setup(
    name='dockerdb',
    version='0.2.0',
    description="TODO Description",
    long_description=readme,
    author="Florian Ludwig",
    author_email='f.ludwig@greyrook.com',
    url='https://github.com/GreyRook/dockerdb',
    packages=[
        'dockerdb',
    ],
    package_dir={'dockerdb':
                 'dockerdb'},
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='dockerdb',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
                'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

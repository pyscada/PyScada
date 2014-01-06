# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import pyscada


CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Scientific/Engineering :: Visualization'
]
setup(
    author=pyscada.__author__,
    author_email="info@martin-schroeder.net",
    name='PyScada',
    version=pyscada.__version__,
    description='An Python, Django based Open Source Scada System',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    url='http://www.martin-schroeder.net/',
    license='GPL version 3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'django>=1.5',
        'pymodbus>=1.2',
        'numpy>=1.6.0',
        'h5py>=2.1.1'
    ],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    zip_safe=False,
    test_suite='runtests.main',
)
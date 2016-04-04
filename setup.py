# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
import pyscada


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Environment :: Console',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: JavaScript',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Scientific/Engineering :: Visualization'
]
setup(
    author=pyscada.__author__,
    author_email="info@martin-schroeder.net",
    name='PyScada',
    version=pyscada.__version__,
    description='An Python, Django based Open Source Scada System',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.martin-schroeder.net/PyScada',
    license='GPL version 3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'django>=1.7,<1.9',
        'pymodbus>=1.2',
        'numpy>=1.6.0',
        'h5py>=2.2.1',
        'psutil>=2.1.1',
        'pillow',
        'python-daemon>=2.0.0'
    ],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    zip_safe=False,
    test_suite='runtests.main',
)

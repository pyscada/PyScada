# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os
from pyscada import core


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Environment :: Console',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Scientific/Engineering :: Visualization'
]
setup(
    author=core.__author__,
    author_email="info@martin-schroeder.net",
    name='PyScada',
    version=core.__version__,
    description='A Python and Django based Open Source SCADA System',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    url='http://www.github.com/trombastic/PyScada',
    license='GPL version 3',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'django<2.3',
        'pymodbus>=1.2',
        'numpy>=1.6.0',
        'h5py>=2.2.1',
        'psutil>=2.1.1',
        'pillow',
        'python-daemon>=2.0.0',
        'pytz',
        'pyserial',
        'channels',
        'asgiref',
        'concurrent',
    ],
    packages=find_packages(exclude=["project", "project.*"]),
    include_package_data=True,
    zip_safe=False,
    test_suite='runtests.main',
    namespace_packages=['pyscada']
)

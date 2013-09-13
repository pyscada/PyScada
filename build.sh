#!/bin/sh

rm -rf build/ 
rm -rf dist/
rm -rf PyScada.egg-info/ 
rm -rf /usr/local/lib/python2.7/site-packages/PyScada-0.1.testing-py2.7.egg 
python setup.py install

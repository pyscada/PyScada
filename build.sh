#!/bin/sh

rm -rf build/ 
rm -rf dist/
rm -rf PyScada.egg-info/ 
rm -rf /usr/local/lib/python2.7/site-packages/PyScada-* 
python setup.py install

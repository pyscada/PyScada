#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
from pyscada.utils import export_xml_config_file
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = 'filename'
    help = 'import config from xml file'

    def handle(self, *args, **options):
        if len(args) < 1:
            self.stdout.write('usage: python manage.py  PyScadaWriteXMLConfig "configfile.xml" \n', ending='')
        elif len(args) == 1:
            export_xml_config_file(args[0])
        else:
            self.stdout.write('usage: python manage.py  PyScadaWriteXMLConfig "configfile.xml" \n" \n', ending='')

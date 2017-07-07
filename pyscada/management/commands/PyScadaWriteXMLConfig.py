#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyscada.utils import export_xml_config_file
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'import config from xml file'
    
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
    
    def handle(self, *args, **options):
        export_xml_config_file(options['filename'][0])
        

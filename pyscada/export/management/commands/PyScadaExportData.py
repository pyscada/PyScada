#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
from pyscada.export.export import export_recordeddata_to_file
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'export data to file'
    def add_arguments(self, parser):
        parser.add_argument('--filename',dest='filename', default=None,  type=str)
        parser.add_argument('--start_id',dest='start_id', default=None, type=str)
        parser.add_argument('--stop_id', dest='stop_id', default=None, type=str)
    
    def handle(self, *args, **options):
        
        if options['filename'] is None:
            export_recordeddata_to_file(options['start_id'],options['stop_id'])
        elif options['filename'] is not None:
            export_recordeddata_to_file(options['start_id'],options['stop_id'],os.path.abspath(options['filename']))
        
        
#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pyscada.export.export import export_recordeddata_to_file
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'export data to file'

    def add_arguments(self, parser):
        parser.add_argument('--filename',dest='filename', default=None,  type=str,
                            help='the filename and path to write to')
        parser.add_argument('--start_time',dest='start_time', default=None, type=str,
                            help='the starting time to begin the export from, can be either unixtimestamp or string in "%d-%b-%Y %H:%M:%S" style')
        parser.add_argument('--stop_time', dest='stop_time', default=None, type=str,
                            help='the last time to export, can be either unixtimestamp or string in "%d-%b-%Y %H:%M:%S" style')
    
    def handle(self, *args, **options):
        
        if options['filename'] is None:
            export_recordeddata_to_file(options['start_time'],options['stop_time'])
        elif options['filename'] is not None:
            export_recordeddata_to_file(options['start_time'],options['stop_time'],os.path.abspath(options['filename']))

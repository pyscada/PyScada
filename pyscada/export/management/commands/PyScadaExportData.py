#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys
from pyscada.export import export_recordeddata_to_file
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = 'filename start_id stop_id'
    help = 'export data to file'

    def handle(self, *args, **options):
        #if len(args) < 1:
        #    self.stdout.write('usage: python manage.py  PyScadaExportData "14-Mar-2014 21:50:00" ["outputfile.mat"] ["16-Mar-2014 21:50:00"]\n', ending='')
        if len(args) == 0:
            export_recordeddata_to_file()
        elif len(args) == 1:
            export_recordeddata_to_file(args[0])
        elif len(args) == 2:
            export_recordeddata_to_file(args[0],None,os.path.abspath(args[0]))
        elif len(args) == 3:
            export_recordeddata_to_file(args[0],args[2],os.path.abspath(args[1]))
        else:
            self.stdout.write('usage: python manage.py  PyScadaExportData "14-Mar-2014 21:50:00" ["outputfile.mat"] ["16-Mar-2014 21:50:00"]\n', ending='')

#!/usr/bin/python
# -*- coding: utf-8 -*- 
import os,sys
from pyscada.export import export_database_to_h5
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = 'filename start_id stop_id'
    help = 'export data to file'

    def handle(self, *args, **options):
        #if len(args) < 1:
        #    self.stdout.write('usage: python manage.py  PyScadaExportData "14-Mar-2014 21:50:00" ["outputfile.mat"] ["16-Mar-2014 21:50:00"]\n', ending='')
        if len(args) == 0:
            export_database_to_h5()
        elif len(args) == 1:
            export_database_to_h5(args[0])
        elif len(args) == 2:
            export_database_to_h5(args[0],os.path.abspath(args[0]))
        elif len(args) == 3:
            export_database_to_h5(args[0],os.path.abspath(args[1]),args[2])
        else:
            self.stdout.write('usage: python manage.py  PyScadaExportData "14-Mar-2014 21:50:00" ["outputfile.mat"] ["16-Mar-2014 21:50:00"]\n', ending='')
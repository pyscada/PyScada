#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyscada.utils.scheduler import Scheduler
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manage the Background Process Daemon for PyScada"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["start", "stop", "restart", "status", "init"],
            nargs="+",
            type=str,
        )

    def handle(self, *args, **options):
        # init scheduler instance
        scheduler = Scheduler(stdout=self.stdout)
        if "start" == options["action"][0]:
            scheduler.start()
        elif "stop" == options["action"][0]:
            scheduler.stop()
        elif "status" == options["action"][0]:
            scheduler.status()
        elif "init" == options["action"][0]:
            scheduler.init_db()
        elif "restart" == options["action"][0]:
            scheduler.stop()
            scheduler.start()

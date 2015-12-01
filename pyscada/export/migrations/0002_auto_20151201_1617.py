# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('export', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportjob',
            name='file_format',
            field=models.CharField(default=b'hdf5', max_length=400, choices=[(b'hdf5', b'Hierarchical Data Format Version 5'), (b'mat', b'Matlab\xc2\xae mat v7.3 compatible file'), (b'CSV_EXCEL', b'Microsoft\xc2\xae Excel\xc2\xae compatible csv file')]),
            preserve_default=True,
        ),
    ]

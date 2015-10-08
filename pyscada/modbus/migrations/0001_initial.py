# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModbusClient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('protocol', models.PositiveSmallIntegerField(default=0, choices=[(0, b'TCP'), (1, b'UDP'), (2, b'serial ASCII'), (3, b'serial RTU')])),
                ('ip_address', models.GenericIPAddressField(default=b'127.0.0.1')),
                ('port', models.CharField(default=b'502', help_text=b'for TCP and UDP enter network port as number (def. 502, for serial ASCII and RTU enter serial port (/dev/pts/13))', max_length=400)),
                ('unit_id', models.PositiveSmallIntegerField(default=0)),
                ('modbus_client', models.OneToOneField(to='pyscada.Client')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModbusVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.PositiveIntegerField()),
                ('function_code_read', models.PositiveSmallIntegerField(default=0, help_text=b'', choices=[(0, b'not selected'), (1, b'coils (FC1)'), (2, b'discrete inputs (FC2)'), (3, b'holding registers (FC3)'), (4, b'input registers (FC4)')])),
                ('modbus_variable', models.OneToOneField(to='pyscada.Variable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

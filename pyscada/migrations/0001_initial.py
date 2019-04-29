# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BackgroundTask',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.FloatField(default=0)),
                ('timestamp', models.FloatField(default=0)),
                ('progress', models.FloatField(default=0)),
                ('load', models.FloatField(default=0)),
                ('min', models.FloatField(default=0)),
                ('max', models.FloatField(default=0)),
                ('done', models.BooleanField(default=False)),
                ('failed', models.BooleanField(default=False)),
                ('pid', models.IntegerField(default=0)),
                ('stop_daemon', models.BooleanField(default=False)),
                ('label', models.CharField(default=b'', max_length=400)),
                ('message', models.CharField(default=b'', max_length=400)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('short_name', models.CharField(default=b'', max_length=400)),
                ('client_type', models.CharField(default='generic', max_length=400, choices=[('modbus', 'Modbus Client'), ('systemstat', 'Monitor Local System')])),
                ('description', models.TextField(default=b'', null=True, verbose_name='Description')),
                ('active', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClientWriteTask',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.FloatField()),
                ('start', models.FloatField(default=0)),
                ('fineshed', models.FloatField(default=0, blank=True)),
                ('done', models.BooleanField(default=False)),
                ('failed', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(default=b'', max_length=400)),
                ('level', models.PositiveSmallIntegerField(default=0, choices=[(0, 'informative'), (1, 'ok'), (2, 'warning'), (3, 'alert')])),
                ('fixed_limit', models.FloatField(default=0, null=True, blank=True)),
                ('limit_type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'value is less than limit'), (1, 'value is less than or equal to the limit'), (2, 'value is greater than the limit'), (3, 'value is greater than or equal to the limit'), (4, 'value equals the limit')])),
                ('action', models.PositiveSmallIntegerField(default=0, choices=[(0, 'just record'), (1, 'record and send mail only wenn event occurs'), (2, 'record and send mail'), (3, 'record, send mail and change variable')])),
                ('new_value', models.FloatField(default=0, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('level', models.IntegerField(default=0, verbose_name='level')),
                ('timestamp', models.FloatField()),
                ('message_short', models.CharField(default=b'', max_length=400, verbose_name='short message')),
                ('message', models.TextField(default=b'', verbose_name='message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailQueue',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('subject', models.TextField(default=b'', blank=True)),
                ('message', models.TextField(default=b'', blank=True)),
                ('mail_from', models.TextField(default='pyscada@martin-schroeder.net', blank=True)),
                ('timestamp', models.FloatField(default=0, blank=True)),
                ('done', models.BooleanField(default=False)),
                ('send_fail_count', models.PositiveSmallIntegerField(default=0, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MailRecipient',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('subject_prefix', models.TextField(default=b'', blank=True)),
                ('message_suffix', models.TextField(default=b'', blank=True)),
                ('to_email', models.EmailField(default=b'', max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedDataBoolean',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedDataCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('version', models.PositiveIntegerField(default=0, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedDataFloat',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedDataInt',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('value', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedEvent',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('active', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Event', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecordedTime',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('timestamp', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('unit', models.CharField(max_length=80, verbose_name='Unit')),
                ('description', models.TextField(default=b'', null=True, verbose_name='Description')),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.SlugField(max_length=80, verbose_name='variable name')),
                ('description', models.TextField(default=b'', verbose_name='Description')),
                ('active', models.BooleanField(default=True)),
                ('writeable', models.BooleanField(default=False)),
                ('record', models.BooleanField(default=True)),
                ('value_class', models.CharField(default='FLOAT64', max_length=15, verbose_name='value_class', choices=[('FLOAT32', 'REAL'), ('FLOAT32', 'SINGLE'), ('FLOAT32', 'FLOAT32'), ('FLOAT64', 'LREAL'), ('FLOAT64', 'FLOAT'), ('FLOAT64', 'FLOAT64'), ('INT32', 'INT32'), ('UINT32', 'UINT32'), ('INT16', 'INT'), ('INT16', 'INT16'), ('UINT16', 'WORD'), ('UINT16', 'UINT'), ('UINT16', 'UINT16'), ('BOOLEAN', 'BOOL'), ('BOOLEAN', 'BOOLEAN')])),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Client', null=True)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Unit', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariableChangeHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('field', models.PositiveSmallIntegerField(default=0, choices=[(0, 'active'), (1, 'writable'), (2, 'value_class'), (3, 'variable_name')])),
                ('old_value', models.TextField(default=b'')),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True)),
                ('variable', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='recordedevent',
            name='time_begin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordedevent',
            name='time_end',
            field=models.ForeignKey(related_name='time_end', on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddataint',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddataint',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddatafloat',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddatafloat',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddatacache',
            name='last_change',
            field=models.ForeignKey(related_name='last_change', on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddatacache',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddatacache',
            name='variable',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddataboolean',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.RecordedTime', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recordeddataboolean',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mailqueue',
            name='mail_recipients',
            field=models.ManyToManyField(to='pyscada.MailRecipient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='mail_recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='pyscada.MailRecipient', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='variable_limit',
            field=models.ForeignKey(related_name='variable_limit', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='pyscada.Variable', help_text='you can choose either an fixed limit or an variable limit that is dependent on the current value of an variable, if you choose a value other then none for varieble limit the fixed limit would be ignored', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='variable_to_change',
            field=models.ForeignKey(related_name='variable_to_change', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clientwritetask',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pyscada.Variable', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='VariableConfigFileImport',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('pyscada.variable',),
        ),
    ]

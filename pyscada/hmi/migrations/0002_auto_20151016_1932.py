# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyscada', '0002_event_hysteresis'),
        ('hmi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessFlowDiagram',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(default='', max_length=400, blank=True)),
                ('background_image', models.ImageField(upload_to='img/', verbose_name='background image', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProcessFlowDiagramItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(default='', max_length=400, blank=True)),
                ('type', models.PositiveSmallIntegerField(default=0, choices=[(0, 'label blue'), (1, 'label light blue'), (2, 'label ok'), (3, 'label warning'), (4, 'label alarm'), (7, 'label alarm inverted'), (5, 'Control Element'), (6, 'Display Value')])),
                ('top', models.PositiveIntegerField(default=0)),
                ('left', models.PositiveIntegerField(default=0)),
                ('width', models.PositiveIntegerField(default=0)),
                ('height', models.PositiveIntegerField(default=0)),
                ('visible', models.BooleanField(default=True)),
                ('variable', models.ForeignKey(default=None, to='pyscada.Variable', on_delete=models.SET_NULL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='processflowdiagram',
            name='process_flow_diagram_items',
            field=models.ManyToManyField(to='hmi.ProcessFlowDiagramItem', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='groupdisplaypermission',
            name='process_flow_diagram',
            field=models.ManyToManyField(to='hmi.ProcessFlowDiagram', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='widget',
            name='process_flow_diagram',
            field=models.ForeignKey(default=None, blank=True, to='hmi.ProcessFlowDiagram', null=True, on_delete=models.SET_NULL),
            preserve_default=True,
        ),
    ]

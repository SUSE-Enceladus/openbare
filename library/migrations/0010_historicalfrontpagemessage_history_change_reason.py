# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-24 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_auto_20170424_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalfrontpagemessage',
            name='history_change_reason',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('from_email', models.TextField(verbose_name='From')),
                ('recipients', models.TextField()),
                ('subject', models.CharField(max_length=120)),
                ('body', models.TextField()),
                ('date_sent', models.DateTimeField(db_index=True, auto_now_add=True)),
            ],
            options={
                'ordering': ('-date_sent',),
            },
        ),
    ]

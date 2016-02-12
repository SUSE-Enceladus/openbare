# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('checked_out_on', models.DateTimeField(auto_now_add=True)),
                ('renewals', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('provider', models.CharField(max_length=254)),
                ('name', models.CharField(max_length=254)),
                ('description', models.TextField()),
                ('max_instances', models.IntegerField(default=1)),
                ('checkout_period_in_days', models.IntegerField(default=14)),
                ('max_renewals', models.IntegerField(default=2)),
                ('plugin_name', models.TextField(default='library.plugins.generic')),
            ],
        ),
        migrations.AddField(
            model_name='instance',
            name='resource',
            field=models.ForeignKey(to='library.Resource'),
        ),
        migrations.AddField(
            model_name='instance',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]

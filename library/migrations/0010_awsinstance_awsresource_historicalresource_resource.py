# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-07-09 21:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0009_auto_20170424_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalResource',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('type', models.CharField(db_index=True, max_length=255)),
                ('acquired', models.DateTimeField(blank=True, null=True)),
                ('preserve', models.DateTimeField(blank=True, null=True)),
                ('reaped', models.BooleanField(default=False)),
                ('released', models.DateTimeField(blank=True, null=True)),
                ('resource_id', models.CharField(max_length=127)),
                ('scope', models.CharField(max_length=63)),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('lendable', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='library.Lendable')),
            ],
            options={
                'verbose_name': 'historical resource',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('library.awsresource', 'aws resource'), ('library.awsinstance', 'aws instance')], db_index=True, max_length=255)),
                ('acquired', models.DateTimeField(blank=True, null=True)),
                ('preserve', models.DateTimeField(blank=True, null=True)),
                ('reaped', models.BooleanField(default=False)),
                ('released', models.DateTimeField(blank=True, null=True)),
                ('resource_id', models.CharField(max_length=127)),
                ('scope', models.CharField(max_length=63)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lendable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='library.Lendable')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AWSResource',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('library.resource',),
        ),
        migrations.CreateModel(
            name='AWSInstance',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('library.awsresource',),
        ),
    ]
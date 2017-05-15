# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-12 20:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_auto_20170424_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagementCommand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=127, unique=True)),
                ('last_success', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('library.awsinstance', 'aws instance')], db_index=True, max_length=255)),
                ('acquired', models.DateTimeField(blank=True, null=True)),
                ('reaped', models.BooleanField(default=False)),
                ('released', models.DateTimeField(blank=True, null=True)),
                ('resource_id', models.CharField(max_length=127)),
                ('scope', models.CharField(max_length=63)),
                ('lendable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='library.Lendable')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AWSInstance',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('library.resource',),
        ),
    ]
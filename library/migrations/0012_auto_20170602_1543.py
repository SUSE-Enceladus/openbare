# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-02 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_resource_preserve'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSResource',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('library.resource',),
        ),
        migrations.AlterField(
            model_name='resource',
            name='type',
            field=models.CharField(choices=[('library.awsresource', 'aws resource'), ('library.awsinstance', 'aws instance')], db_index=True, max_length=255),
        ),
    ]
# Generated by Django 3.0.8 on 2022-09-29 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0011_mc_itemgsthsncode_commonid'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_pagefieldmaster',
            name='InValidMsg',
            field=models.CharField(default=1, max_length=300),
            preserve_default=False,
        ),
    ]

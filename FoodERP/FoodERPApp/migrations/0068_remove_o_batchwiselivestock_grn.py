# Generated by Django 3.0.8 on 2022-12-01 10:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0067_auto_20221201_1046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='GRN',
        ),
    ]

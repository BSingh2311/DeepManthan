# Generated by Django 3.0.8 on 2022-11-30 08:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0049_tc_grnitems_systembatchdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='UpdatedBy',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='UpdatedOn',
        ),
    ]

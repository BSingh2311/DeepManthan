# Generated by Django 3.0.8 on 2022-10-04 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0023_auto_20221003_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mc_itemcategorydetails',
            name='Category',
        ),
        migrations.RemoveField(
            model_name='mc_itemcategorydetails',
            name='CategoryType',
        ),
        migrations.RemoveField(
            model_name='mc_itemcategorydetails',
            name='SubCategory',
        ),
    ]

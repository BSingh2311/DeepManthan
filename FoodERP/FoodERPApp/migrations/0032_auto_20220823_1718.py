# Generated by Django 3.0.8 on 2022-08-23 17:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0031_remove_m_parties_customerdivision'),
    ]

    operations = [
        migrations.DeleteModel(
            name='M_ItemsGroup',
        ),
        migrations.AlterModelTable(
            name='m_productsubcategory',
            table='M_ItemsGroup',
        ),
    ]

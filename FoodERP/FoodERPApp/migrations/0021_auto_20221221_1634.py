# Generated by Django 3.0.8 on 2022-12-21 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0020_auto_20221221_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_vehicles',
            name='CreatedBy',
        ),
        migrations.RemoveField(
            model_name='m_vehicles',
            name='CreatedOn',
        ),
        migrations.RemoveField(
            model_name='m_vehicles',
            name='UpdatedBy',
        ),
        migrations.RemoveField(
            model_name='m_vehicles',
            name='UpdatedOn',
        ),
    ]

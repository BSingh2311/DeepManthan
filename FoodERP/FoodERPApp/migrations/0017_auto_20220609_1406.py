# Generated by Django 3.0.8 on 2022-06-09 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0016_auto_20220609_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_employess',
            name='DesignationID',
        ),
        migrations.DeleteModel(
            name='M_Designations',
        ),
        migrations.DeleteModel(
            name='M_Employess',
        ),
    ]

# Generated by Django 3.0.8 on 2022-12-07 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0086_m_billofmaterial_isdelete'),
    ]

    operations = [
        migrations.RenameField(
            model_name='m_billofmaterial',
            old_name='EstimatedOutput',
            new_name='EstimatedOutputQty',
        ),
    ]

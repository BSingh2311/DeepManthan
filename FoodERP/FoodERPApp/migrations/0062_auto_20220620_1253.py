# Generated by Django 3.0.8 on 2022-06-20 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0061_m_employees_c_companies'),
    ]

    operations = [
        migrations.RenameField(
            model_name='m_employees',
            old_name='C_Companies',
            new_name='Companies',
        ),
    ]

# Generated by Django 3.0.8 on 2023-06-02 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0030_m_cities'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_cities',
            name='District',
        ),
    ]

# Generated by Django 3.0.8 on 2023-05-29 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0014_auto_20230529_1511'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_importfields',
            name='Company',
        ),
    ]

# Generated by Django 3.0.8 on 2022-08-22 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0024_auto_20220822_1328'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='m_items',
            name='ItemGroup',
        ),
        migrations.RemoveField(
            model_name='m_items',
            name='image',
        ),
    ]

# Generated by Django 3.0.8 on 2022-06-28 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0104_auto_20220628_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m_parties',
            name='PhoneNo',
            field=models.CharField(max_length=10),
        ),
    ]

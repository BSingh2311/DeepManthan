# Generated by Django 3.0.8 on 2022-11-01 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_items',
            name='CanBePurchase',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='m_items',
            name='CanBeSold',
            field=models.BooleanField(default=False),
        ),
    ]

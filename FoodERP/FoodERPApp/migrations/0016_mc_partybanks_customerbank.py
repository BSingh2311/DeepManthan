# Generated by Django 3.0.8 on 2023-04-17 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0015_auto_20230415_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_partybanks',
            name='CustomerBank',
            field=models.BooleanField(default=False),
        ),
    ]

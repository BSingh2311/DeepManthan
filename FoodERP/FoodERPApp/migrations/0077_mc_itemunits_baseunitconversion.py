# Generated by Django 3.0.8 on 2023-02-07 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0076_auto_20230206_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='mc_itemunits',
            name='BaseUnitConversion',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
    ]

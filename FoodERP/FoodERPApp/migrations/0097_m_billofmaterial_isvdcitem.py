# Generated by Django 3.0.8 on 2023-02-15 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0096_m_pricelist_calculationpath'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_billofmaterial',
            name='IsVDCItem',
            field=models.BooleanField(default=False),
        ),
    ]

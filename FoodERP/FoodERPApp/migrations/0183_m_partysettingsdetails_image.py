# Generated by Django 3.0.8 on 2023-10-16 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0182_auto_20231013_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_partysettingsdetails',
            name='Image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='Images\\PartyRelatedImages'),
        ),
    ]

# Generated by Django 3.0.8 on 2023-06-22 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0029_remove_mc_settingsdetails_party'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_invoiceuploads',
            name='EwayBillNo',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
    ]

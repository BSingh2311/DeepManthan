# Generated by Django 3.0.8 on 2022-06-29 07:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0117_auto_20220629_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='tc_orderitems',
            name='CreatedOn',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tc_orderitems',
            name='GSTAmount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
            preserve_default=False,
        ),
    ]

# Generated by Django 3.0.8 on 2023-09-16 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0163_l_transactiondatelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_stock',
            name='BatchCodeID',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

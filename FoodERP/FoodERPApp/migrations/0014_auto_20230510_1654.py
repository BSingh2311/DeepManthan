# Generated by Django 3.0.8 on 2023-05-10 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0013_auto_20230510_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='o_batchwiselivestock',
            name='PurchaseReturn',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BatchWiseLiveStockReturnID', to='FoodERPApp.T_PurchaseReturn'),
        ),
    ]

# Generated by Django 3.0.8 on 2023-04-07 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0029_auto_20230407_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='t_receipts',
            name='ReceiptMode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='Receiptmode', to='FoodERPApp.M_GeneralMaster'),
        ),
        migrations.AddField(
            model_name='t_receipts',
            name='ReceiptType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ReceiptType', to='FoodERPApp.M_GeneralMaster'),
        ),
    ]

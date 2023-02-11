# Generated by Django 3.0.8 on 2023-02-11 13:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0086_t_vdcchallan_tc_vdcchallanitems_tc_vdcchallanreferences'),
    ]

    operations = [
        migrations.RenameField(
            model_name='t_vdcchallan',
            old_name='FullChallanNumber',
            new_name='FullInvoiceNumber',
        ),
        migrations.RenameField(
            model_name='t_vdcchallan',
            old_name='ChallanDate',
            new_name='InvoiceDate',
        ),
        migrations.RenameField(
            model_name='t_vdcchallan',
            old_name='ChallanNumber',
            new_name='InvoiceNumber',
        ),
        migrations.AlterField(
            model_name='tc_vdcchallanreferences',
            name='VDCChallan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VDCChallanReferences', to='FoodERPApp.T_VDCChallan'),
        ),
    ]

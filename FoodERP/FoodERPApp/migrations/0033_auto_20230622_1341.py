# Generated by Django 3.0.8 on 2023-06-22 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0032_auto_20230622_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='AckNo',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EInvoiceCanceledBy',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EInvoiceCreatedBy',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EInvoicePdf',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EwayBillCanceledBy',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EwayBillCreatedBy',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EwayBillNo',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='EwayBillUrl',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='Invoice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='InvoiceUploads', to='FoodERPApp.T_Invoices'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='Irn',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceuploads',
            name='QRCodeUrl',
            field=models.CharField(max_length=500, null=True),
        ),
    ]

# Generated by Django 3.0.8 on 2023-06-21 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0022_auto_20230621_1204'),
    ]

    operations = [
        migrations.CreateModel(
            name='TC_InvoiceUploads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('IRN_ACKNO', models.CharField(max_length=500)),
                ('InvoicePdf', models.DateTimeField(auto_now_add=True)),
                ('QRCodeUrl', models.CharField(max_length=500)),
                ('EwayBillNo', models.CharField(max_length=500)),
                ('EwayBillUrl', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField()),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('CancelBy', models.IntegerField()),
                ('CanceledOn', models.DateTimeField(auto_now=True)),
                ('IsCancel', models.BooleanField(default=False)),
                ('Invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='InvoiceUploads', to='FoodERPApp.T_Invoices')),
            ],
            options={
                'db_table': 'TC_InvoiceUploads',
            },
        ),
    ]

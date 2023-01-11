# Generated by Django 3.0.8 on 2023-01-11 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0031_auto_20230109_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='TC_InvoicesReferences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'TC_InvoicesReferences',
            },
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitembatches',
            name='Invoice',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitembatches',
            name='InvoiceItem',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitembatches',
            name='Item',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitembatches',
            name='Unit',
        ),
        migrations.RenameField(
            model_name='tc_invoiceitems',
            old_name='HSNCode',
            new_name='BatchCode',
        ),
        migrations.RemoveField(
            model_name='mc_partyaddress',
            name='AddressType',
        ),
        migrations.RemoveField(
            model_name='t_invoices',
            name='Order',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitems',
            name='QtyInBox',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitems',
            name='QtyInKg',
        ),
        migrations.RemoveField(
            model_name='tc_invoiceitems',
            name='QtyInNo',
        ),
        migrations.AddField(
            model_name='tc_invoiceitems',
            name='BatchDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mc_partyaddress',
            name='FSSAIExipry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mc_partyaddress',
            name='FSSAINo',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='mc_partyaddress',
            name='fssaidocument',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='t_invoices',
            name='Customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='InvoicesCustomer', to='FoodERPApp.M_Parties'),
        ),
        migrations.AlterField(
            model_name='t_invoices',
            name='Party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='InvoicesParty', to='FoodERPApp.M_Parties'),
        ),
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='DiscountType',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='tc_invoiceitems',
            name='MRP',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.DeleteModel(
            name='M_AddressTypes',
        ),
        migrations.DeleteModel(
            name='TC_InvoiceItemBatches',
        ),
        migrations.AddField(
            model_name='tc_invoicesreferences',
            name='Invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FoodERPApp.T_Invoices'),
        ),
        migrations.AddField(
            model_name='tc_invoicesreferences',
            name='Order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='FoodERPApp.T_Orders'),
        ),
    ]

# Generated by Django 3.0.8 on 2023-01-13 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0037_auto_20230113_1119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='BatchCode',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='BatchDate',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='GST',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='ItemExpiryDate',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='MRP',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='Rate',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='SystemBatchCode',
        ),
        migrations.RemoveField(
            model_name='o_batchwiselivestock',
            name='SystemBatchDate',
        ),
        migrations.CreateModel(
            name='O_LiveBatches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('BatchDate', models.DateField(blank=True, null=True)),
                ('BatchCode', models.CharField(max_length=500)),
                ('SystemBatchDate', models.DateField()),
                ('SystemBatchCode', models.CharField(max_length=500)),
                ('MRP', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
                ('Rate', models.DecimalField(decimal_places=2, max_digits=15, null=True)),
                ('ItemExpiryDate', models.DateField()),
                ('GST', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ObatchwiseItemGst', to='FoodERPApp.M_GSTHSNCode')),
            ],
        ),
    ]

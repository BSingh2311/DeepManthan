# Generated by Django 3.0.8 on 2022-10-03 12:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0019_m_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='MC_SubGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField(default=False)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(default=False)),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
                ('Group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='Group', to='FoodERPApp.M_Group')),
            ],
            options={
                'db_table': 'MC_SubGroup',
            },
        ),
    ]

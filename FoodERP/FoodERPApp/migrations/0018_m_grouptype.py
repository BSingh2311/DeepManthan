# Generated by Django 3.0.8 on 2022-10-03 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0017_m_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='M_GroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=500)),
                ('CreatedBy', models.IntegerField(default=False)),
                ('CreatedOn', models.DateTimeField(auto_now_add=True)),
                ('UpdatedBy', models.IntegerField(default=False)),
                ('UpdatedOn', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'M_GroupType',
            },
        ),
    ]

# Generated by Django 3.0.8 on 2022-06-18 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0045_remove_m_items_itemgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='m_items',
            name='ItemGroup',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='FoodERPApp.M_ItemsGroup'),
            preserve_default=False,
        ),
    ]

# Generated by Django 3.0.8 on 2022-12-12 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FoodERPApp', '0095_tc_materialissueitems'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tc_materialissueitems',
            name='Item',
        ),
        migrations.RemoveField(
            model_name='tc_materialissueitems',
            name='MaterialIssue',
        ),
        migrations.RemoveField(
            model_name='tc_materialissueitems',
            name='Unit',
        ),
        migrations.RemoveField(
            model_name='tc_materialissueworkorders',
            name='MaterialIssue',
        ),
        migrations.RemoveField(
            model_name='tc_materialissueworkorders',
            name='WorkOrder',
        ),
        migrations.DeleteModel(
            name='T_MaterialIssue',
        ),
        migrations.DeleteModel(
            name='TC_MaterialIssueItems',
        ),
        migrations.DeleteModel(
            name='TC_MaterialIssueWorkOrders',
        ),
    ]

# Generated by Django 3.2.5 on 2021-07-03 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tradetransaction',
            name='temp',
        ),
        migrations.AlterField(
            model_name='tradetransaction',
            name='player_a_discord_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='tradetransaction',
            name='player_b_discord_id',
            field=models.BigIntegerField(),
        ),
    ]
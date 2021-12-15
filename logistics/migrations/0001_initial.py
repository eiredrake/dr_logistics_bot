# Generated by Django 4.0 on 2021-12-15 15:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TradeTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateTimeField(auto_created=True)),
                ('player_a_discord_id', models.BigIntegerField()),
                ('player_a_display_name', models.CharField(max_length=255, verbose_name='trader')),
                ('player_b_discord_id', models.BigIntegerField()),
                ('player_b_display_name', models.CharField(max_length=255, verbose_name='recipient')),
                ('items', models.CharField(max_length=500)),
                ('transaction_completed', models.DateTimeField(blank=True, null=True)),
                ('comments', models.TextField(blank=True, max_length=501, null=True)),
                ('flagged', models.BooleanField(default=False)),
                ('flag_reason', models.TextField(blank=True, max_length=255, null=True)),
                ('flagged_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'logistics_tradetransaction',
            },
        ),
        migrations.CreateModel(
            name='ActionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_start', models.DateTimeField(auto_created=True, verbose_name='start')),
                ('action_completed', models.DateTimeField(blank=True, null=True)),
                ('interrupted', models.BooleanField(blank=True, null=True)),
                ('actor_discord_id', models.BigIntegerField()),
                ('actor_display_name', models.CharField(max_length=255, verbose_name='actor')),
                ('action_type', models.SmallIntegerField(blank=True, choices=[(1, 'brew'), (2, 'build'), (3, 'cook'), (4, 'consume'), (5, 'do'), (6, 'farm'), (7, 'forage'), (8, 'hunt'), (9, 'inject'), (10, 'salvage'), (11, 'smoke'), (12, 'spend'), (13, 'trailblaze'), (14, 'upgrade'), (15, 'use'), (16, 'repair')], null=True)),
                ('items', models.CharField(max_length=255)),
                ('quantity', models.SmallIntegerField(blank=True, null=True)),
                ('mind_cost', models.SmallIntegerField(blank=True, null=True)),
                ('time_cost', models.IntegerField(blank=True, null=True)),
                ('resolve_cost', models.SmallIntegerField(blank=True, null=True)),
                ('materials', models.TextField(blank=True, max_length=500, null=True)),
                ('commentary', models.TextField(blank=True, max_length=500, null=True)),
                ('processed', models.BooleanField(default=False)),
                ('flagged', models.BooleanField(default=False)),
                ('flag_reason', models.TextField(blank=True, max_length=255, null=True)),
                ('flagged_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
            options={
                'db_table': 'logistics_actionrecord',
            },
        ),
    ]

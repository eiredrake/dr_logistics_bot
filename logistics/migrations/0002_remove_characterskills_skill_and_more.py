# Generated by Django 4.0 on 2021-12-13 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characterskills',
            name='skill',
        ),
        migrations.RemoveField(
            model_name='characterskills',
            name='skills_character',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.RemoveField(
            model_name='researchrequest',
            name='flagged_by',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='skill_levels',
        ),
        migrations.RemoveField(
            model_name='skilllevels',
            name='level_skill',
        ),
        migrations.DeleteModel(
            name='Character',
        ),
        migrations.DeleteModel(
            name='CharacterSkills',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
        migrations.DeleteModel(
            name='ResearchRequest',
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.DeleteModel(
            name='SkillLevels',
        ),
    ]

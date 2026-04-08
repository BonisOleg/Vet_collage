"""
Re-sync migration: brings Django's migration state in line with the database
columns that were added by ghost migrations (0003_course_subtitle_speakers_program_currency
and 0004_seed_nutrition_course) which exist in django_migrations but have no
corresponding files.

All operations here are state-only (database_operations=[]) because the
columns already exist in the SQLite database.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_course_bunny_library_id_course_instructor_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name='course',
                    name='currency',
                    field=models.CharField(default='UAH', max_length=3, verbose_name='Валюта'),
                ),
                migrations.AddField(
                    model_name='course',
                    name='subtitle',
                    field=models.CharField(blank=True, default='', max_length=512, verbose_name='Підзаголовок'),
                ),
                migrations.AddField(
                    model_name='course',
                    name='materials_access_note',
                    field=models.TextField(blank=True, default='', verbose_name='Умови доступу до матеріалів'),
                ),
            ],
        ),
    ]

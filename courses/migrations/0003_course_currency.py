from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_course_bunny_library_id_course_instructor_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE courses_course
                ADD COLUMN IF NOT EXISTS currency VARCHAR(3) NOT NULL DEFAULT 'UAH';
            """,
            reverse_sql="ALTER TABLE courses_course DROP COLUMN IF EXISTS currency;",
            state_operations=[
                migrations.AddField(
                    model_name='course',
                    name='currency',
                    field=models.CharField(default='UAH', max_length=3, verbose_name='Валюта'),
                ),
            ],
        ),
    ]

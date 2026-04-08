from django.db import migrations, models

_FIX_ORPHANED_NOT_NULL = """
DO $$
DECLARE
    col RECORD;
BEGIN
    FOR col IN
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'courses_course'
          AND table_schema = 'public'
          AND is_nullable = 'NO'
          AND column_default IS NULL
          AND column_name NOT IN (
              'id','title','slug','description','price',
              'duration_hours','level','is_active','is_popular',
              'requires_membership','created_at',
              'currency','materials_access_note'
          )
    LOOP
        EXECUTE format(
            'ALTER TABLE courses_course ALTER COLUMN %I SET DEFAULT %L',
            col.column_name,
            CASE
                WHEN col.data_type IN ('text','character varying') THEN ''
                WHEN col.data_type = 'boolean'                    THEN 'false'
                ELSE '0'
            END
        );
    END LOOP;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [('courses', '0003_course_currency')]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE courses_course
                ADD COLUMN IF NOT EXISTS materials_access_note TEXT NOT NULL DEFAULT '';
            """ + _FIX_ORPHANED_NOT_NULL,
            reverse_sql="ALTER TABLE courses_course DROP COLUMN IF EXISTS materials_access_note;",
            state_operations=[
                migrations.AddField(
                    model_name='course',
                    name='materials_access_note',
                    field=models.TextField(
                        blank=True, default='',
                        verbose_name='Умови доступу до матеріалів',
                    ),
                ),
            ],
        ),
    ]

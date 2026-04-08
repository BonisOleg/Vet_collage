from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_resync_existing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='module_number',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Номер модуля'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='module_title',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Назва модуля'),
        ),
        migrations.CreateModel(
            name='CourseInstructor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='ПІБ')),
                ('role', models.CharField(blank=True, max_length=255, verbose_name='Роль/посада')),
                ('bio', models.TextField(blank=True, verbose_name='Біографія')),
                ('photo', models.ImageField(blank=True, upload_to='instructors/', verbose_name='Фото')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='instructors',
                    to='courses.course',
                    verbose_name='Курс',
                )),
            ],
            options={
                'verbose_name': 'Спікер',
                'verbose_name_plural': 'Спікери',
                'ordering': ['order'],
            },
        ),
    ]

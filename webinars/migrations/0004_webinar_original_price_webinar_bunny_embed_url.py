from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0003_webinar_audience'),
    ]

    operations = [
        migrations.AddField(
            model_name='webinar',
            name='original_price',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Ціна до знижки — відображається закресленою поруч із поточною ціною',
                max_digits=10,
                null=True,
                verbose_name='Стара ціна',
            ),
        ),
        migrations.AddField(
            model_name='webinar',
            name='bunny_embed_url',
            field=models.URLField(
                blank=True,
                help_text=(
                    'Скопіюйте URL-адресу iframe з Bunny.net Stream → Share → Embed. '
                    'Якщо заповнено — використовується замість Library ID + Video ID.'
                ),
                max_length=500,
                verbose_name='Посилання для вставки відео (Bunny.net)',
            ),
        ),
    ]

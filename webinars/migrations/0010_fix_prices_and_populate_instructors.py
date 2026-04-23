# Migration: fix webinar prices and populate instructors

from django.db import migrations


INSTRUCTORS = [
    {
        'name': 'Ткач Єгор Кирилович',
        'role': 'Засновник та голова наукової ради UCVN',
        'bio': (
            'Ветеринарний дієтолог із близько п\'ятирічним практичним досвідом, '
            'експерт ESVCN та атестований AAHA Champion Nutrition. Пройшов навчання '
            'у дипломатів ESVCN, сертифікований слухач лекцій WSAVA та провідних '
            'міжнародних експертів, зокрема Cecilia Villaverde Haro та Georgia Woods-Lee. '
            'Один із провідних фахівців країни та досвідчений лектор, який особливо '
            'цінує науку й сучасні дослідження у своїй роботі.'
        ),
        'order': 0,
    },
    {
        'name': 'Добиш Ксенія Миколаївна',
        'role': 'Член наукової ради UCVN',
        'bio': (
            'Ветеринарна дієтологиня з понад п\'ятирічним практичним досвідом, '
            'експерт ESVCN, здобувачка ступеня MSc in Animal Nutrition (Університет '
            'Глазго), членкиня WSAVA та AVA. Сертифікована NAVC Pet Nutrition Coach, '
            'пройшла навчання та стажування у дипломатів ECVCN, сертифікована слухачка '
            'лекцій WSAVA з ветеринарної дієтології. Одна з провідних фахівців країни '
            'та досвідчена лекторка з глибоким практичним досвідом.'
        ),
        'order': 1,
    },
]


def fix_prices_and_add_instructors(apps, schema_editor):
    Webinar = apps.get_model('webinars', 'Webinar')
    WebinarInstructor = apps.get_model('webinars', 'WebinarInstructor')

    for webinar in Webinar.objects.all():
        webinar.price = 80.00
        webinar.original_price = 100.00
        webinar.currency = 'EUR'
        webinar.save()

        for data in INSTRUCTORS:
            WebinarInstructor.objects.get_or_create(
                webinar=webinar,
                name=data['name'],
                defaults={
                    'role': data['role'],
                    'bio': data['bio'],
                    'order': data['order'],
                },
            )


def reverse_migration(apps, schema_editor):
    Webinar = apps.get_model('webinars', 'Webinar')
    WebinarInstructor = apps.get_model('webinars', 'WebinarInstructor')

    for webinar in Webinar.objects.all():
        webinar.price = 200.00
        webinar.original_price = None
        webinar.save()

    WebinarInstructor.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0009_webinarinstructor'),
    ]

    operations = [
        migrations.RunPython(fix_prices_and_add_instructors, reverse_migration),
    ]

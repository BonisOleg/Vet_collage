# Generated migration to populate webinar content

from django.db import migrations


def populate_webinar_data(apps, schema_editor):
    Webinar = apps.get_model('webinars', 'Webinar')
    
    webinar_data = [
        {
            'id': 1,
            'price': 200.00,
            'currency': 'EUR',
            'what_you_learn': [
                'Основи ветеринарної дієтології',
                'Анатомія та фізіологія харчування',
                'Роль білків, жирів, вітамінів та мінералів у раціоні',
                'Аналіз комерційних кормів',
            ],
            'materials_access_note': '1 рік',
        },
        {
            'id': 2,
            'price': 200.00,
            'currency': 'EUR',
            'what_you_learn': [
                'Основи ветеринарної дієтології',
                'Анатомія та фізіологія харчування',
                'Роль білків, жирів, вітамінів та мінералів у раціоні',
                'Аналіз комерційних кормів',
            ],
            'materials_access_note': '1 рік',
        },
        {
            'id': 3,
            'price': 200.00,
            'currency': 'EUR',
            'what_you_learn': [
                'Основи ветеринарної дієтології',
                'Анатомія та фізіологія харчування',
                'Роль білків, жирів, вітамінів та мінералів у раціоні',
                'Аналіз комерційних кормів',
            ],
            'materials_access_note': '1 рік',
        },
    ]
    
    for data in webinar_data:
        try:
            webinar = Webinar.objects.get(id=data['id'])
            webinar.price = data['price']
            webinar.currency = data['currency']
            webinar.what_you_learn = data['what_you_learn']
            webinar.materials_access_note = data['materials_access_note']
            webinar.save()
        except Webinar.DoesNotExist:
            pass


def reverse_populate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0007_webinar_materials_access_note_webinar_what_you_learn'),
    ]

    operations = [
        migrations.RunPython(populate_webinar_data, reverse_populate),
    ]

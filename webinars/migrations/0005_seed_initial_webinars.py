"""
Data migration: seed the 3 hardcoded "Нутриціологія" webinars
that were previously shown as Figma mock cards in the {% empty %} block.

Covers are intentionally left blank — upload them via Django admin.
The slugs are set manually because Django's default slugify() strips
Cyrillic characters and would produce an empty string for Ukrainian titles.
"""
from decimal import Decimal

from django.db import migrations


WEBINARS = [
    {
        'title': 'Нутриціологія',
        'slug': 'nutrytsiolohiia',
        'description': (
            'Вебінар призначений для тих, які хочуть освоїти основи та розуміти, '
            'як харчування впливає на тварин.'
        ),
        'price': Decimal('80.00'),
        'original_price': Decimal('100.00'),
        'audience': 'owners',
    },
    {
        'title': 'Нутриціологія',
        'slug': 'nutrytsiolohiia-2',
        'description': (
            'Вебінар призначений для тих, які хочуть освоїти основи та розуміти, '
            'як харчування впливає на тварин.'
        ),
        'price': Decimal('80.00'),
        'original_price': Decimal('100.00'),
        'audience': 'owners',
    },
    {
        'title': 'Нутриціологія',
        'slug': 'nutrytsiolohiia-3',
        'description': (
            'Вебінар призначений для тих, які хочуть освоїти основи та розуміти, '
            'як харчування впливає на тварин.'
        ),
        'price': Decimal('80.00'),
        'original_price': Decimal('100.00'),
        'audience': 'owners',
    },
]


def seed_webinars(apps, schema_editor):
    Webinar = apps.get_model('webinars', 'Webinar')
    for data in WEBINARS:
        Webinar.objects.get_or_create(
            slug=data['slug'],
            defaults={
                'title': data['title'],
                'description': data['description'],
                'price': data['price'],
                'original_price': data['original_price'],
                'audience': data['audience'],
                'duration_min': 60,
                'is_active': True,
                'is_free': False,
                'requires_membership': False,
            },
        )


def unseed_webinars(apps, schema_editor):
    Webinar = apps.get_model('webinars', 'Webinar')
    slugs = [w['slug'] for w in WEBINARS]
    Webinar.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('webinars', '0004_webinar_original_price_webinar_bunny_embed_url'),
    ]

    operations = [
        migrations.RunPython(seed_webinars, reverse_code=unseed_webinars),
    ]

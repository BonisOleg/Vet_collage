"""
Management command: upload_media_to_bunny

Uploads all existing local media files (ImageFields) to Bunny Storage.
Idempotent: skips files that already exist on the remote Storage Zone.

Usage:
    python manage.py upload_media_to_bunny
    python manage.py upload_media_to_bunny --dry-run
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


def _storage_base_url(username: str, region: str) -> str:
    region = region.lower().strip()
    if region in ('', 'ny'):
        return f'https://storage.bunnycdn.com/{username}'
    return f'https://{region}.storage.bunnycdn.com/{username}'


def _iter_image_paths() -> Iterator[str]:
    """Yield non-empty ImageField values (relative paths) from all models."""
    from blog.models import Article
    from courses.models import Course, CourseInstructor
    from webinars.models import Webinar, WebinarInstructor

    specs = [
        (Course, 'cover'),
        (CourseInstructor, 'photo'),
        (Webinar, 'cover'),
        (WebinarInstructor, 'photo'),
        (Article, 'cover'),
    ]
    seen: set[str] = set()
    for model, field_name in specs:
        filter_kwargs = {f'{field_name}__gt': ''}
        for obj in model.objects.filter(**filter_kwargs).only(field_name):
            path: str = getattr(obj, field_name).name
            if path and path not in seen:
                seen.add(path)
                yield path


class Command(BaseCommand):
    help = 'Upload local media files to Bunny Storage (idempotent one-time migration).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without making any changes.',
        )

    def handle(self, *args, **options):
        dry_run: bool = options['dry_run']

        username: str = settings.BUNNY_USERNAME
        password: str = settings.BUNNY_PASSWORD
        region: str = settings.BUNNY_REGION or 'de'

        if not username or not password:
            raise CommandError(
                'BUNNY_USERNAME and BUNNY_PASSWORD must be set in environment.'
            )

        media_root = Path(settings.MEDIA_ROOT)
        base_url = _storage_base_url(username, region)

        if dry_run:
            self.stdout.write(self.style.WARNING('[dry-run] No files will be uploaded.'))

        uploaded = skipped = missing = errors = 0

        for rel_path in _iter_image_paths():
            local_file = media_root / rel_path
            remote_url = f'{base_url}/{rel_path}'

            if not local_file.exists():
                self.stdout.write(
                    self.style.WARNING(f'  MISSING locally: {rel_path}')
                )
                missing += 1
                continue

            # Check whether the file already exists on Bunny Storage.
            head_resp = requests.head(
                remote_url,
                headers={'AccessKey': password},
                timeout=15,
            )
            if head_resp.status_code == 200:
                self.stdout.write(f'  EXISTS (skip):  {rel_path}')
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f'  WOULD UPLOAD:   {rel_path}'))
                uploaded += 1
                continue

            # Upload the file.
            with open(local_file, 'rb') as fh:
                put_resp = requests.put(
                    remote_url,
                    data=fh,
                    headers={
                        'AccessKey': password,
                        'Content-Type': 'application/octet-stream',
                    },
                    timeout=120,
                )

            if put_resp.ok:
                self.stdout.write(self.style.SUCCESS(f'  UPLOADED:       {rel_path}'))
                uploaded += 1
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f'  FAILED ({put_resp.status_code}): {rel_path} — {put_resp.text[:120]}'
                    )
                )
                errors += 1

        verb = 'Would upload' if dry_run else 'Uploaded'
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {verb}: {uploaded}, skipped: {skipped}, '
                f'missing locally: {missing}, errors: {errors}.'
            )
        )

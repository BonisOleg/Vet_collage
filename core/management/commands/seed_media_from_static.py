"""
Management command: seed_media_from_static

Copies webinar cover images from static/images/ into media/ and updates
empty ImageField records in the database. Idempotent by default — skips
any record that already has a value set (override with --force).

Usage:
    python manage.py seed_media_from_static
    python manage.py seed_media_from_static --force
"""
from __future__ import annotations

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from webinars.models import Webinar, WebinarInstructor

# slug → filename inside static/images/
WEBINAR_COVERS: dict[str, str] = {
    'nutrytsiolohiia':   'webinar-photo-1.webp',
    'nutrytsiolohiia-2': 'webinar-photo-2.webp',
    'nutrytsiolohiia-3': 'webinar-photo-3.webp',
}

# name fragment (case-insensitive) → relative path inside MEDIA_ROOT
INSTRUCTOR_PHOTOS: dict[str, str] = {
    'ткач':   'instructors/tkach.webp',
    'добиш':  'instructors/dovbysh.webp',
}


class Command(BaseCommand):
    help = 'Seed DB ImageField paths from static/images/ (idempotent).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite even records that already have a value.',
        )

    def handle(self, *args, **options):
        force: bool = options['force']
        static_images = Path(settings.BASE_DIR) / 'static' / 'images'
        media_root = Path(settings.MEDIA_ROOT)

        updated = skipped = errors = 0

        # ── Webinar covers ────────────────────────────────────────────────
        self.stdout.write('--- Webinar covers ---')
        for slug, filename in WEBINAR_COVERS.items():
            try:
                webinar = Webinar.objects.get(slug=slug)
            except Webinar.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  SKIP (not in DB): webinar slug={slug}'))
                skipped += 1
                continue

            if webinar.cover and not force:
                self.stdout.write(f'  SKIP (already set): {slug} → {webinar.cover.name}')
                skipped += 1
                continue

            src = static_images / filename
            if not src.exists():
                self.stdout.write(self.style.ERROR(f'  ERROR: source not found: {src}'))
                errors += 1
                continue

            dest_dir = media_root / 'webinars' / 'covers'
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / filename

            shutil.copy2(src, dest)
            db_path = f'webinars/covers/{filename}'
            webinar.cover = db_path
            webinar.save(update_fields=['cover'])

            self.stdout.write(self.style.SUCCESS(f'  OK: {slug} → {db_path}'))
            updated += 1

        # ── WebinarInstructor photos ──────────────────────────────────────
        self.stdout.write('--- Instructor photos ---')
        for instructor in WebinarInstructor.objects.all():
            if instructor.photo and not force:
                self.stdout.write(
                    f'  SKIP (already set): {instructor.name} → {instructor.photo.name}'
                )
                skipped += 1
                continue

            name_lower = instructor.name.lower()
            db_path: str | None = None
            for fragment, rel_path in INSTRUCTOR_PHOTOS.items():
                if fragment in name_lower:
                    db_path = rel_path
                    break

            if db_path is None:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP (no mapping): {instructor.name}')
                )
                skipped += 1
                continue

            media_file = media_root / db_path
            if not media_file.exists():
                # Try to copy from static/images/ as fallback
                filename = media_file.name
                src = static_images / filename
                if src.exists():
                    media_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, media_file)
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ERROR: file not found: {media_file}')
                    )
                    errors += 1
                    continue

            instructor.photo = db_path
            instructor.save(update_fields=['photo'])
            self.stdout.write(
                self.style.SUCCESS(f'  OK: {instructor.name} (id={instructor.id}) → {db_path}')
            )
            updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. Updated: {updated}, skipped: {skipped}, errors: {errors}.'
            )
        )

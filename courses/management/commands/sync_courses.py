"""Idempotent sync of Category, Course, Lesson, and CourseInstructor from JSON."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from courses.models import Category, Course, CourseInstructor, Enrollment, Lesson

User = get_user_model()

_LEVELS = frozenset({'beginner', 'intermediate', 'advanced'})


class Command(BaseCommand):
    help = 'Sync categories, courses, and lessons from JSON (update_or_create by slug).'

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            '--file',
            dest='file',
            required=True,
            help='Path to JSON (see courses/data/sync_courses.example.json).',
        )
        parser.add_argument(
            '--enroll-email',
            dest='enroll_email',
            default='',
            help='With --course-slug: ensure Enrollment for this email.',
        )
        parser.add_argument(
            '--course-slug',
            dest='course_slug',
            default='',
            help='Course slug for optional Enrollment.',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        path = Path(str(options['file'])).expanduser().resolve()
        if not path.is_file():
            raise CommandError(f'File not found: {path}')

        raw = path.read_text(encoding='utf-8')
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CommandError(f'Invalid JSON: {exc}') from exc

        enroll_email = (options['enroll_email'] or '').strip()
        course_slug = (options['course_slug'] or '').strip()
        if bool(enroll_email) ^ bool(course_slug):
            raise CommandError('Provide both --enroll-email and --course-slug, or neither.')

        self._validate_root(data)

        cat_n = self._sync_categories(data.get('categories', []))
        course_n, lesson_counts = self._sync_courses(data['courses'])
        lesson_n = lesson_counts
        enroll_msg = ''
        if enroll_email:
            enroll_msg = ' ' + self._enroll(enroll_email, course_slug)

        self.stdout.write(
            self.style.SUCCESS(
                f'Synced categories: {cat_n}, courses: {course_n}, '
                f'lessons: {lesson_n[0]} (+{lesson_n[1]} deleted), '
                f'instructors: {lesson_n[2]}.'
                f'{enroll_msg}'
            )
        )

    def _validate_root(self, data: Any) -> None:
        if not isinstance(data, dict):
            raise CommandError('Root value must be a JSON object.')
        courses = data.get('courses')
        if not isinstance(courses, list):
            raise CommandError('Key "courses" must be an array.')
        cats = data.get('categories', [])
        if cats is not None and not isinstance(cats, list):
            raise CommandError('Key "categories" must be an array when present.')

    def _sync_categories(self, items: list[Any]) -> int:
        n = 0
        for raw in items:
            if not isinstance(raw, dict):
                raise CommandError('Each category must be an object.')
            name = raw.get('name')
            slug = raw.get('slug')
            if not name or not slug:
                raise CommandError('Each category needs "name" and "slug".')
            Category.objects.update_or_create(
                slug=str(slug),
                defaults={'name': str(name)},
            )
            n += 1
        return n

    def _sync_courses(self, items: list[Any]) -> tuple[int, tuple[int, int, int]]:
        course_n = 0
        lesson_n: tuple[int, int, int] = (0, 0, 0)  # synced, deleted, instructors
        for raw in items:
            if not isinstance(raw, dict):
                raise CommandError('Each course must be an object.')
            slug = raw.get('slug')
            title = raw.get('title')
            description = raw.get('description')
            price_raw = raw.get('price')
            if not slug or not title or description is None or price_raw is None:
                raise CommandError(
                    'Each course needs "slug", "title", "description", and "price".',
                )
            try:
                price = Decimal(str(price_raw))
            except (InvalidOperation, ValueError) as exc:
                raise CommandError(f'Invalid price for course "{slug}": {price_raw}') from exc

            category_slug = raw.get('category_slug') or raw.get('category')
            category = None
            if category_slug:
                category = Category.objects.filter(slug=str(category_slug)).first()
                if category is None:
                    raise CommandError(
                        f'Unknown category_slug "{category_slug}" for course "{slug}". '
                        'Define the category in "categories" first.',
                    )

            level = str(raw.get('level', 'beginner'))
            if level not in _LEVELS:
                raise CommandError(
                    f'Invalid level "{level}" for course "{slug}" '
                    f'(use beginner|intermediate|advanced).',
                )

            instructor = None
            instructor_username = raw.get('instructor_username')
            if instructor_username:
                instructor = User.objects.filter(
                    username=str(instructor_username),
                ).first()
                if instructor is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skip instructor: user "{instructor_username}" not found '
                            f'(course "{slug}").',
                        ),
                    )

            what_you_learn = raw.get('what_you_learn', [])
            if what_you_learn is None:
                what_you_learn = []
            if not isinstance(what_you_learn, list):
                raise CommandError(f'what_you_learn must be a list for course "{slug}".')
            wyf: list[str] = []
            for item in what_you_learn:
                if not isinstance(item, str):
                    raise CommandError(
                        f'what_you_learn items must be strings for course "{slug}".',
                    )
                wyf.append(item)

            duration_hours = int(raw.get('duration_hours', 0))
            if duration_hours < 0:
                raise CommandError(f'duration_hours must be >= 0 for course "{slug}".')

            course, _created = Course.objects.update_or_create(
                slug=str(slug),
                defaults={
                    'title': str(title),
                    'subtitle': str(raw.get('subtitle', '') or ''),
                    'category': category,
                    'description': str(description),
                    'price': price,
                    'currency': str(raw.get('currency', 'UAH') or 'UAH'),
                    'duration_hours': duration_hours,
                    'level': level,
                    'is_active': bool(raw.get('is_active', True)),
                    'is_popular': bool(raw.get('is_popular', False)),
                    'requires_membership': bool(raw.get('requires_membership', False)),
                    'what_you_learn': wyf,
                    'bunny_library_id': str(raw.get('bunny_library_id', '') or ''),
                    'promo_bunny_video_id': str(raw.get('promo_bunny_video_id', '') or ''),
                    'materials_access_note': str(raw.get('materials_access_note', '') or ''),
                    'instructor': instructor,
                },
            )
            course_n += 1

            lessons = raw.get('lessons', [])
            if lessons is not None and not isinstance(lessons, list):
                raise CommandError(f'"lessons" must be an array for course "{slug}".')
            synced_lesson_n = 0
            synced_slugs: list[str] = []
            for les_raw in lessons or []:
                synced_lesson_n += self._sync_lesson(course, les_raw, str(slug))
                synced_slugs.append(str(les_raw['slug']))

            deleted_n, _ = course.lessons.exclude(slug__in=synced_slugs).delete()
            lesson_n = (lesson_n[0] + synced_lesson_n, lesson_n[1] + deleted_n, lesson_n[2])

            instructors_raw = raw.get('instructors', [])
            if instructors_raw is not None and not isinstance(instructors_raw, list):
                raise CommandError(f'"instructors" must be an array for course "{slug}".')
            instr_n = self._sync_instructors(course, instructors_raw or [], str(slug))
            lesson_n = (lesson_n[0], lesson_n[1], lesson_n[2] + instr_n)

        return course_n, lesson_n

    def _sync_lesson(
        self,
        course: Course,
        raw: Any,
        course_slug: str,
    ) -> int:
        if not isinstance(raw, dict):
            raise CommandError(f'Each lesson must be an object (course "{course_slug}").')
        title = raw.get('title')
        slug = raw.get('slug')
        if not title or not slug:
            raise CommandError(
                f'Each lesson needs "title" and "slug" (course "{course_slug}").',
            )
        order = int(raw.get('order', 0))
        duration_seconds = int(raw.get('duration_seconds', 0))
        if duration_seconds < 0:
            raise CommandError(
                f'duration_seconds must be >= 0 (lesson "{slug}", course "{course_slug}").',
            )
        module_number = int(raw.get('module_number', 1))
        if module_number < 1:
            raise CommandError(
                f'module_number must be >= 1 (lesson "{slug}", course "{course_slug}").',
            )
        Lesson.objects.update_or_create(
            course=course,
            slug=str(slug),
            defaults={
                'title': str(title),
                'description': str(raw.get('description', '') or ''),
                'bunny_video_id': str(raw.get('bunny_video_id', '') or ''),
                'duration_seconds': duration_seconds,
                'order': order,
                'module_number': module_number,
                'module_title': str(raw.get('module_title', '') or ''),
                'is_preview': bool(raw.get('is_preview', False)),
            },
        )
        return 1

    def _sync_instructors(
        self,
        course: Course,
        items: list[Any],
        course_slug: str,
    ) -> int:
        course.instructors.all().delete()
        for idx, raw in enumerate(items):
            if not isinstance(raw, dict):
                raise CommandError(
                    f'Each instructor must be an object (course "{course_slug}").',
                )
            name = raw.get('name')
            if not name:
                raise CommandError(
                    f'Each instructor needs "name" (course "{course_slug}").',
                )
            CourseInstructor.objects.create(
                course=course,
                name=str(name),
                role=str(raw.get('role', '') or ''),
                bio=str(raw.get('bio', '') or ''),
                order=int(raw.get('order', idx)),
            )
        return len(items)

    def _enroll(self, email: str, slug: str) -> str:
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise CommandError(f'No user with email "{email}".')
        course = Course.objects.filter(slug=slug).first()
        if course is None:
            raise CommandError(f'No course with slug "{slug}" (sync file first).')
        _obj, created = Enrollment.objects.get_or_create(user=user, course=course)
        return 'Enrollment created.' if created else 'Enrollment already existed.'

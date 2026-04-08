import json
import tempfile
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from courses.models import Category, Course, Enrollment, Lesson

User = get_user_model()


class CourseDetailBackLinkTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.course = Course.objects.create(
            title='Тестовий курс',
            slug='test-back-link-course',
            description='Опис',
            price=Decimal('1.00'),
            is_active=True,
        )

    def test_back_link_default_goes_to_course_list(self) -> None:
        url = reverse('courses:detail', kwargs={'slug': self.course.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('courses:list'))
        self.assertContains(response, 'Назад до курсів')
        self.assertNotContains(response, 'Назад до моїх курсів')

    def test_back_link_from_cabinet_goes_to_cabinet_courses_tab(self) -> None:
        url = reverse('courses:detail', kwargs={'slug': self.course.slug})
        response = self.client.get(f'{url}?from=cabinet')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/accounts/cabinet/')
        self.assertContains(response, 'tab=courses')
        self.assertContains(response, 'Назад до моїх курсів')

    def test_unknown_from_value_uses_catalog_back(self) -> None:
        url = reverse('courses:detail', kwargs={'slug': self.course.slug})
        response = self.client.get(f'{url}?from=evil')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('courses:list'))
        self.assertContains(response, 'Назад до курсів')


def _sync_test_payload() -> dict:
    return {
        'categories': [{'name': 'Кат тест', 'slug': 'sync-cat'}],
        'courses': [
            {
                'title': 'Курс sync',
                'slug': 'sync-course-slug',
                'category_slug': 'sync-cat',
                'description': 'Опис sync',
                'price': '49.99',
                'duration_hours': 3,
                'level': 'intermediate',
                'is_active': True,
                'is_popular': True,
                'requires_membership': False,
                'what_you_learn': ['a', 'b'],
                'lessons': [
                    {
                        'title': 'Урок A',
                        'slug': 'lesson-a',
                        'order': 0,
                        'duration_seconds': 120,
                        'is_preview': True,
                    },
                    {
                        'title': 'Урок B',
                        'slug': 'lesson-b',
                        'order': 1,
                        'bunny_video_id': 'vid-1',
                    },
                ],
            },
        ],
    }


class SyncCoursesCommandTests(TestCase):
    def test_sync_creates_and_updates_idempotently(self) -> None:
        payload = _sync_test_payload()
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8',
        ) as tmp:
            json.dump(payload, tmp)
            path = tmp.name

        try:
            call_command('sync_courses', file=path)
            self.assertEqual(Category.objects.count(), 1)
            self.assertEqual(Course.objects.count(), 1)
            self.assertEqual(Lesson.objects.count(), 2)
            course = Course.objects.get(slug='sync-course-slug')
            self.assertEqual(course.title, 'Курс sync')
            self.assertEqual(course.price, Decimal('49.99'))
            self.assertEqual(course.what_you_learn, ['a', 'b'])

            payload['courses'][0]['title'] = 'Оновлено'
            payload['courses'][0]['lessons'][0]['title'] = 'Урок A2'
            with Path(path).open('w', encoding='utf-8') as f:
                json.dump(payload, f)

            call_command('sync_courses', file=path)
            self.assertEqual(Category.objects.count(), 1)
            self.assertEqual(Course.objects.count(), 1)
            self.assertEqual(Lesson.objects.count(), 2)
            course.refresh_from_db()
            self.assertEqual(course.title, 'Оновлено')
            self.assertEqual(
                Lesson.objects.get(course=course, slug='lesson-a').title,
                'Урок A2',
            )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_enrollment_get_or_create(self) -> None:
        user = User.objects.create_user(
            username='sync-user',
            email='Sync@Example.com',
            password='x',
        )
        payload = _sync_test_payload()
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8',
        ) as tmp:
            json.dump(payload, tmp)
            path = tmp.name

        try:
            call_command(
                'sync_courses',
                file=path,
                enroll_email='sync@example.com',
                course_slug='sync-course-slug',
            )
            self.assertTrue(
                Enrollment.objects.filter(user=user, course__slug='sync-course-slug').exists(),
            )
            call_command(
                'sync_courses',
                file=path,
                enroll_email='sync@example.com',
                course_slug='sync-course-slug',
            )
            self.assertEqual(Enrollment.objects.filter(user=user).count(), 1)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_enroll_requires_user(self) -> None:
        from django.core.management.base import CommandError

        payload = _sync_test_payload()
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8',
        ) as tmp:
            json.dump(payload, tmp)
            path = tmp.name

        try:
            with self.assertRaises(CommandError) as ctx:
                call_command(
                    'sync_courses',
                    file=path,
                    enroll_email='nobody@example.com',
                    course_slug='sync-course-slug',
                )
            self.assertIn('No user with email', str(ctx.exception))
        finally:
            Path(path).unlink(missing_ok=True)

    def test_partial_enroll_args_rejected(self) -> None:
        from django.core.management.base import CommandError

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8',
        ) as tmp:
            json.dump({'categories': [], 'courses': []}, tmp)
            path = tmp.name

        try:
            with self.assertRaises(CommandError):
                call_command(
                    'sync_courses',
                    file=path,
                    enroll_email='a@b.c',
                )
        finally:
            Path(path).unlink(missing_ok=True)

    def test_unknown_category_errors(self) -> None:
        from django.core.management.base import CommandError

        payload = _sync_test_payload()
        payload['courses'][0]['category_slug'] = 'missing'
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8',
        ) as tmp:
            json.dump(payload, tmp)
            path = tmp.name

        try:
            with self.assertRaises(CommandError):
                call_command('sync_courses', file=path)
        finally:
            Path(path).unlink(missing_ok=True)

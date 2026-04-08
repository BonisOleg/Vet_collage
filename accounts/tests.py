from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from courses.models import Course, Enrollment

User = get_user_model()


class CabinetCoursesContextTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username='u@test.com',
            email='u@test.com',
            password='testpass123',
        )

    def test_cabinet_shows_enrolled_course_title(self) -> None:
        course = Course.objects.create(
            title='Курс запису користувача',
            slug='cabinet-enrolled-course',
            description='Опис',
            price=Decimal('1.00'),
            is_popular=False,
        )
        Enrollment.objects.create(user=self.user, course=course)
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:cabinet'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, course.title)

    @override_settings(CABINET_CONTINUE_FALLBACK_COURSE_SLUGS=())
    def test_cabinet_fallback_popular_when_not_enrolled(self) -> None:
        popular = Course.objects.create(
            title='Популярний курс',
            slug='cabinet-popular-course',
            description='Опис',
            price=Decimal('2.00'),
            is_popular=True,
        )
        Course.objects.create(
            title='Інший курс',
            slug='cabinet-other-course',
            description='Опис',
            price=Decimal('3.00'),
            is_popular=False,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:cabinet'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, popular.title)
        self.assertNotContains(response, 'Інший курс')

    @override_settings(CABINET_CONTINUE_FALLBACK_COURSE_SLUGS=())
    def test_cabinet_empty_state_when_no_courses_to_suggest(self) -> None:
        Course.objects.create(
            title='Не популярний',
            slug='cabinet-not-popular',
            description='Опис',
            price=Decimal('4.00'),
            is_popular=False,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:cabinet'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Немає курсів для продовження перегляду')
        self.assertContains(response, reverse('courses:list'))

    @override_settings(CABINET_CONTINUE_FALLBACK_COURSE_SLUGS=('cabinet-slug-fallback',))
    def test_cabinet_fallback_by_configured_slug_order(self) -> None:
        Course.objects.create(
            title='Перший за slug',
            slug='cabinet-slug-fallback',
            description='Опис',
            price=Decimal('5.00'),
            is_popular=False,
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:cabinet'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Перший за slug')

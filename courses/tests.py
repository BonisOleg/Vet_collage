from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from courses.models import Course


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

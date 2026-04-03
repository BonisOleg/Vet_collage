import json
import time
from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from core.services.bunny import BunnyNetService
from .models import Category, Course, Enrollment, Lesson

_AGENT_DEBUG_LOG = Path(__file__).resolve().parents[1] / '.cursor' / 'debug-625a1a.log'


def _agent_debug_log(hypothesis_id, message, data, run_id='post-fix'):
    # #region agent log
    try:
        payload = {
            'sessionId': '625a1a',
            'hypothesisId': hypothesis_id,
            'location': 'courses/views.py:CourseListView',
            'message': message,
            'data': data,
            'timestamp': int(time.time() * 1000),
            'runId': run_id,
        }
        _AGENT_DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_AGENT_DEBUG_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload, ensure_ascii=False) + '\n')
    except OSError:
        pass
    # #endregion


class CourseOverviewView(LoginRequiredMixin, DetailView):
    """
    Course learning overview page (Ознайомлення).
    Shown to enrolled users before they start watching lessons.
    URL: /courses/<slug>/learn/
    """
    model = Course
    template_name = 'pages/courses/overview.html'
    context_object_name = 'course'
    login_url = '/accounts/login/'

    def get_queryset(self):
        return Course.objects.filter(is_active=True).prefetch_related('lessons')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object
        lessons = course.lessons.all()

        ctx['lessons'] = lessons
        ctx['first_lesson'] = lessons.first()
        ctx['is_enrolled'] = Enrollment.objects.filter(
            user=self.request.user, course=course,
        ).exists()
        ctx['progress_percent'] = 0  # No progress tracking model yet
        return ctx


class CourseListView(ListView):
    model = Course
    template_name = 'pages/courses/list.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        qs = Course.objects.filter(is_active=True).select_related('category')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        search = self.request.GET.get('q', '').strip()
        sort = self.request.GET.get('sort', '')

        if category:
            qs = qs.filter(category__slug=category)
        if level:
            qs = qs.filter(level=level)
        membership = self.request.GET.get('membership')
        if membership == 'members':
            qs = qs.filter(requires_membership=True)
        elif membership == 'all':
            qs = qs.filter(requires_membership=False)
        if search:
            qs = qs.filter(title__icontains=search)

        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'popular': '-is_popular',
        }
        if sort in sort_map:
            qs = qs.order_by(sort_map[sort])

        # #region agent log
        try:
            total = qs.count()
            head = list(qs[:5].values_list('id', 'price'))
        except Exception:
            total, head = -1, []
        _agent_debug_log(
            'H1',
            'queryset_after_filters',
            {'sort': sort, 'total_count': total, 'id_price_head': head},
        )
        _agent_debug_log(
            'H2',
            'sort_param_received',
            {'sort': sort, 'raw_get_sort': self.request.GET.get('sort')},
        )
        # #endregion

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # #region agent log
        try:
            cl = ctx.get('courses')
            page_len = len(cl) if cl is not None else None
        except Exception:
            page_len = None
        _agent_debug_log(
            'H1',
            'paginated_courses_on_page',
            {
                'page_len': page_len,
                'sort': self.request.GET.get('sort', ''),
            },
        )
        # #endregion
        ctx['categories'] = Category.objects.all()
        ctx['active_category'] = self.request.GET.get('category', '')
        ctx['active_membership'] = self.request.GET.get('membership', '')
        ctx['active_level'] = self.request.GET.get('level', '')
        ctx['active_sort'] = self.request.GET.get('sort', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        ctx['levels'] = Course.LEVEL_CHOICES
        ctx['sort_options'] = [
            ('newest', 'Найновіші'),
            ('price_asc', 'Ціна ↑'),
            ('price_desc', 'Ціна ↓'),
            ('popular', 'Популярні'),
        ]
        if self.request.headers.get('HX-Request'):
            self.template_name = 'pages/courses/partials/course_grid.html'
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'pages/courses/detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(is_active=True).select_related(
            'category', 'instructor',
        ).prefetch_related('lessons')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        ctx['lessons'] = course.lessons.all()
        ctx['is_enrolled'] = False
        ctx['stripe_key'] = settings.STRIPE_PUBLISHABLE_KEY

        if user.is_authenticated:
            ctx['is_enrolled'] = Enrollment.objects.filter(
                user=user, course=course,
            ).exists()

        return ctx


class LessonView(LoginRequiredMixin, DetailView):
    template_name = 'pages/courses/lesson.html'
    context_object_name = 'lesson'
    login_url = '/accounts/login/'

    def get_object(self, queryset=None):
        course = get_object_or_404(
            Course, slug=self.kwargs['course_slug'], is_active=True,
        )
        lesson = get_object_or_404(
            Lesson, course=course, slug=self.kwargs['lesson_slug'],
        )

        is_enrolled = Enrollment.objects.filter(
            user=self.request.user, course=course,
        ).exists()

        if not lesson.is_preview and not is_enrolled:
            raise Http404('Доступ лише для записаних на курс')

        self._course = course
        self._is_enrolled = is_enrolled
        return lesson

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self._course
        lesson = self.object

        ctx['course'] = course
        ctx['lessons'] = course.lessons.all()
        ctx['is_enrolled'] = self._is_enrolled

        if lesson.bunny_video_id:
            library_id = course.bunny_library_id or settings.BUNNY_LIBRARY_ID
            if settings.BUNNY_TOKEN_AUTH_KEY:
                ctx['video_embed_url'] = BunnyNetService.generate_signed_url(
                    video_id=lesson.bunny_video_id,
                    library_id=library_id,
                )
            else:
                ctx['video_embed_url'] = BunnyNetService.get_embed_url(
                    video_id=lesson.bunny_video_id,
                    library_id=library_id,
                    responsive=True,
                )

        prev_lessons = course.lessons.filter(order__lt=lesson.order).order_by('-order')
        next_lessons = course.lessons.filter(order__gt=lesson.order).order_by('order')
        ctx['prev_lesson'] = prev_lessons.first()
        ctx['next_lesson'] = next_lessons.first()
        ctx['progress_percent'] = 0  # No progress tracking model yet

        return ctx

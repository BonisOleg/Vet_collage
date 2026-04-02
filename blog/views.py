from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Article, BlogCategory


def _user_has_membership(user) -> bool:
    if not user.is_authenticated:
        return False
    try:
        return hasattr(user, 'membership') and user.membership.is_active
    except Exception:
        return False


class ArticleListView(ListView):
    model = Article
    context_object_name = 'articles'
    paginate_by = 12

    def get(self, request, *args, **kwargs):
        self._is_member = _user_has_membership(request.user)
        self._has_filter = bool(
            request.GET.get('audience') or
            request.GET.get('category') or
            request.GET.get('q', '').strip()
        )
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.headers.get('HX-Request'):
            return ['pages/blog/partials/article_list.html']
        if self._has_filter:
            return ['pages/blog/list_new.html']
        return ['pages/blog/list.html']

    def get_queryset(self):
        # Landing page doesn't use the queryset (uses owners_cards/vets_cards from context)
        if not getattr(self, '_has_filter', False):
            return Article.objects.none()

        qs = Article.objects.filter(is_published=True).select_related('category')
        if not self._is_member:
            qs = qs.filter(requires_membership=False)

        audience = self.request.GET.get('audience', '')
        category = self.request.GET.get('category', '')
        q = self.request.GET.get('q', '').strip()

        if audience:
            qs = qs.filter(category__audience=audience)
        if category:
            qs = qs.filter(category__slug=category)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q))

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        is_member = getattr(self, '_is_member', False)
        has_filter = getattr(self, '_has_filter', False)

        ctx['user_has_membership'] = is_member
        ctx['has_filter'] = has_filter

        # Audience / category metadata for breadcrumbs and filter bar
        audience = self.request.GET.get('audience', '')
        category_slug = self.request.GET.get('category', '')
        ctx['current_audience'] = audience
        ctx['current_category_slug'] = category_slug

        audience_label_map = {
            'owners': 'Для власників улюбленців',
            'vets': 'Для ветеринарних лікарів',
        }
        ctx['audience_label'] = audience_label_map.get(audience, 'Статті')

        # Categories for topic filter bar
        cat_qs = BlogCategory.objects.all()
        if audience:
            cat_qs = cat_qs.filter(audience=audience)
        ctx['categories'] = cat_qs

        if not has_filter:
            # Landing page: supply 4 owner cards and 4 vet cards
            base_qs = Article.objects.filter(
                is_published=True,
            ).select_related('category')

            ctx['owners_cards'] = base_qs.filter(
                category__audience='owners',
            ).order_by('-published_at')[:4]

            vets_qs = base_qs.filter(category__audience='vets')
            if not is_member:
                vets_qs = vets_qs.filter(requires_membership=False)
            ctx['vets_cards'] = vets_qs.order_by('-published_at')[:4]

        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'pages/blog/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(is_published=True).select_related(
            'category', 'author',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        article = self.object
        has_access = not article.requires_membership or _user_has_membership(user)
        ctx['has_access'] = has_access

        if not has_access and article.content:
            preview_length = min(len(article.content), 500)
            cut = article.content[:preview_length]
            last_space = cut.rfind(' ')
            if last_space > 0:
                cut = cut[:last_space]
            ctx['content_preview'] = cut + '...'
        else:
            ctx['content_preview'] = ''

        # Approximate read time at 200 words per minute
        word_count = len(article.content.split()) if article.content else 0
        ctx['read_time'] = max(1, word_count // 200)

        ctx['related_articles'] = (
            Article.objects.filter(
                is_published=True,
                category=article.category,
            ).exclude(pk=article.pk).select_related('category')[:4]
            if article.category else []
        )

        return ctx
